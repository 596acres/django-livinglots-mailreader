import re

from django.conf import settings

from livinglots import get_lot_model
from livinglots_usercontent.notes.models import Note


class MailReader(object):
    from_name_regex = '(.+?)\s.+'
    from_name_pattern = re.compile(from_name_regex)

    cutoff_line_pattern = '.*%s.*' % settings.MAILREADER_REPLY_PREFIX

    gmail_prefix = re.compile('.*On .+ wrote:.*')

    # These line patterns gathered using emails received and some tips as
    # suggested here:
    #  http://stackoverflow.com/questions/278788/parse-email-content-from-quoted-reply
    #  http://stackoverflow.com/questions/824205/while-processing-an-email-reply-how-can-i-ignore-any-email-client-specifics-th
    reply_prefixes = (
        # Gmail, Yahoo
        gmail_prefix, 

        # Hotmail
        re.compile('^Date:.*'),

        # Outlook Express
        re.compile('^.*---+.*'),

        # Outlook
        re.compile('^.*___+.*'),

        # common mobile signature
        re.compile('^Sent from my .+'),
    )

    def get_name(self, address):
        """Try to get an acceptable name from an email address."""
        try:
            name = self.from_name_pattern.match(address).group(1)
        except Exception:
            name = address.split('@')[0]
        return name

    def should_read(self, from_address=None, to_address=None, subject=None,
                    payloads=None, **kwargs):
        """Should this reader read this mail?"""
        return from_address not in settings.MAILREADER_IGNORE_FROM

    def read(self, from_address=None, to_address=None, subject=None,
             payloads=None, **kwargs):
        """
        Attempt to read the given mail. Return True if successful, False
        otherwise.
        """
        return False

    def parse_message(self, from_address=None, to_address=None, subject=None,
                      payloads=None, verbose=False, **kwargs):
        """
        Parse message from given payloads, including removing any client-added
        reply text.
        """
        combined_payloads = '\r\n'.join(payloads)

        if verbose:
            print 'Starting with:'
            print '=============='
            print combined_payloads

        text = self.strip_reply(from_address, combined_payloads)

        if verbose:
            print 'Ended up with:'
            print '=============='
            print text

        return text

    def remove_lines_after(self, lines, pattern):
        for i, line in enumerate(lines):
            if re.match(pattern, line):
                return lines[:i]
            elif re.match(pattern, ''.join(lines[i:i + 2])):
                # Gmail prefix, in particular, might span multiple lines
                return lines[:i]
        return lines

    def strip_reply(self, from_address, payload_text):
        """
        Try to get the text that the sender sent. Since the email will likely
        be in response to another email, we have to try to get rid of the
        original message and any extra text the sender's email client put
        between the sender's message and the original.
        """
        lines = payload_text.split('\r\n')
        try:
            # Use our cutoff line, which is added to messages that will be
            # replied to, to get rid of most of the quoted text.
            lines = self.remove_lines_after(lines, self.cutoff_line_pattern)

            # chop off empty lines at the end
            while lines[-1] == '':
                lines = lines[:-1]

            # Now chop off common signatures and lines prefixed to replied-to
            # messages.
            if '@gmail.com' in from_address:
                # gmail wraps these lines often
                gmail_test = ''.join(lines[-2:])
                if re.match(self.gmail_prefix, gmail_test):
                    lines = lines[:-2]
            for prefix in self.reply_prefixes:
                lines = self.remove_lines_after(lines, prefix)

        except Exception:
            pass
        return '\n'.join(lines).strip()


class NotesMailReader(MailReader):
    """
    A MailReader that looks for emails that should be turned into notes on a 
    Living Lots site for a particular lot.
    """
    lot_id_regex = '(?:.*\s+)?<?lot\+(\d+)@.+>?'
    lot_id_pattern = re.compile(lot_id_regex)

    def should_read(self, to_address=None, **kwargs):
        if not super(NotesMailReader, self).should_read(to_address=to_address, **kwargs):
            return False
        # TODO rate limiting, by user
        return 'lot' in to_address

    def get_lot(self, to_address):
        """
        Get the lot using the address the message was sent to, which should
        include an ID.
        """
        try:
            lot_id = self.lot_id_pattern.match(to_address).group(1)
            return get_lot_model().objects.get(pk=lot_id)
        except Exception:
            return None

    def read(self, from_address=None, to_address=None, **kwargs):
        lot = self.get_lot(to_address)
        if not lot:
            return False

        text = self.parse_message(from_address=from_address,
                                  to_address=to_address, **kwargs)

        # Don't post empty notes!
        if not text:
            return False

        note = Note(
            added_by_name=self.get_name(from_address),
            content_object=lot,
            text=text,
        )
        note.save()
        return True

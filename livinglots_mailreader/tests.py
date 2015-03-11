from django.test import TestCase

from .readers import MailReader, NotesMailReader


class MailReaderTest(TestCase):

    def setUp(self):
        self.reader = MailReader()

    def test_strip_reply_gmail(self):
        text = "Hi this is my text\r\nOn Thursday, October 23, 2014 2:14 PM, Test Person <test2@gmail.com> wrote:\r\n> Blah blah blah"
        stripped = self.reader.strip_reply('test@gmail.com', text)
        self.assertEqual('Hi this is my text', stripped)

    def test_strip_reply_gmail_multiline(self):
        text = """Test via email.\r\n\r\nOn Tue, Mar 3, 2015 at 12:48 AM, Living Lots NYC Lot 56073 <\r\nlot+56073@livinglotsnyc.org> wrote:\r\n\r\n> Greetings. There has been a change to something you are organizing.\r\n>\r\n> Eric wrote "Hi again" on Staten Island block 7494, lot 8. View it at\r\n> http://livinglotsnyc.org/lot/5074940008/\r\n>\r\n> --\r\n>\r\n> You're receiving this because you are listed as an organizer on Staten\r\n> Island block 7494, lot 8: http://livinglotsnyc.org/lot/5074940008/.\r\n>\r\n>"""

        stripped = self.reader.strip_reply('test@gmail.com', text)
        self.assertEqual('Test via email.', stripped)

    def test_should_read(self):
        self.assertTrue(self.reader.should_read('test@gmail.com'))

    def test_get_name(self):
        self.assertEqual('Jim', self.reader.get_name('Jim Test <test@gmail.com>'))

    def test_get_name_no_first_name(self):
        self.assertEqual('test', self.reader.get_name('test@gmail.com'))


class NotesMailReaderTest(TestCase):

    def setUp(self):
        self.reader = NotesMailReader()

    def test_should_read_no_lot(self):
        self.assertFalse(self.reader.should_read('test@gmail.com'))

    def test_should_read_lot(self):
        self.assertTrue(self.reader.should_read('lot+1234@livinglots.org'))

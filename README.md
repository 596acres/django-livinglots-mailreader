# django-livinglots-mailreader

Reads your mail. Meant to be used in conjunction with 596 Acres' Living Lots,
but could potentially be used in other contexts.

## Install

Use pip.

## Configure

This package expects to see the following Django settings:

* `MAILREADER_HOST`: The mail host
* `MAILREADER_HOST_USER`: The mail username
* `MAILREADER_HOST_PASSWORD`: The mail password
* `MAILREADER_IGNORE_FROM`: A list of email addresses to ignore emails from
* `MAILREADER_REPLY_PREFIX`: A string that will likely be present in incoming
  messages and marks the beginning of a replied-to message. Everything after
  this can safely be ignored.

## License

django-livinglots-mailreader is released under the GNU [Affero General Public 
License, version 3](http://www.gnu.org/licenses/agpl.html).

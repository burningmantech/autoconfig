These are some of the tasks the BM IT team felt would be useful for
next year; 

- [ ] **ARP Management**: Control how radio's connect to autoconf server.
- [ ] **Async IO**: Live feedback to User as radio's are updated.
- [ ] **Robust Updates**: Update radio outside of web browser scope.
- [ ] **Testing**: Is autoconf easy for you and does it work with your radio?

This is more detail on each task:

**ARP Management**: 

On the playa we had a huge problem last year with radio's that are able to
associate with the autoconf server but aren't able to do things like
negotiate a SSH session and/or don't allow login using default IP. The
idea we had hoped would work was that radio's would connect (on .20),
we would apply a different IP in the 192.168.1.x range and then let
them sit out there until we are able to configure them. 

Our initial method of trying to deal with "bad actors", was to remove
their ARP entry from the ARP table if we weren't able to communicate with
them within a set amount of time. We used the 'arp' command to do this.
The problem is that the ARP entries are re-negotiated fairly quickly
and while it helped to alleviate the problem to some extent, it certainly
did not solve the problem. 

A better solution would be something that better controls how the ARP
table is populated, and we can do this on either the computer or on a
"smart" switch.

**Async IO**:

The update process for radio's is slow as it is a two step process. The
first thing we do is that we upgrade the firmware such that all radio's
are using the same firmware. We then apply a configuration to the radio.

It would be nice if we were able to provide the participants with status
as this process updates. 

**Robust Updates**:

We never want radio's in a halfway state when attempting an
autoconfiguration. Currently a radio can get stuck due to connectivity
issues and we may be able to improve on a current process by doing
a better job of managing the update outside of the scope of a flask
session. 

**Testing**:

Probably the most important thing you can do is to test the autoconfiguration
tool. We want to know about both success stories as well as the failures. 

Feedback to BRC-wifi list. 








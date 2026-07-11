# Lesson 6: Networks and the Internet

## What Is a Network

A computer network connects devices so they can exchange data. A local area network
(LAN) covers a small area such as a home or office; a wide area network (WAN) spans
cities or continents. The internet is a global network of networks: independent
networks agree to exchange traffic using shared protocols, so any connected device can
reach any other.

## Packets

Data travels across networks in packets. A packet is a small chunk of data — typically
around a kilobyte — carrying headers that record its source address, destination
address, and sequence position. A large file is split into many packets that may take
different routes across the network and arrive out of order; the receiving device
reassembles them into the original data. Packet switching makes networks resilient:
if one route fails, packets flow around the failure.

## IP Addresses and Routing

Every device on the internet has an IP address that identifies it, much as a street
address identifies a building. IPv4 addresses are four numbers between 0 and 255, such
as 192.168.4.12; because IPv4 addresses are running out, the newer IPv6 provides a
vastly larger address space. Routers are devices that read each packet's destination
address and forward the packet one step closer to it. A packet typically crosses many
routers between source and destination.

## The Domain Name System

People remember names, not numbers. The Domain Name System (DNS) translates
human-readable domain names such as example.edu into IP addresses. When a browser
visits a website, it first queries DNS to resolve the name, then connects to the
returned IP address. DNS is a distributed, hierarchical directory — no single server
holds every name.

## The Web and HTTP

The World Wide Web runs on top of the internet. A browser requests a page using the
Hypertext Transfer Protocol (HTTP): it sends a request to a web server, and the server
responds with the page content, usually written in HTML. Each request-response pair is
independent, which keeps the protocol simple. URLs identify resources: the scheme
(https), the domain name, and the path together tell the browser what to fetch and how.

## Encryption and HTTPS

Data crossing a network can be intercepted, so sensitive traffic is encrypted. HTTPS
is HTTP protected by encryption: the browser and server agree on keys and encrypt
every request and response, so an eavesdropper sees only scrambled bytes. The padlock
icon in a browser indicates an HTTPS connection. Encryption protects confidentiality
(others cannot read the data) and integrity (tampering is detectable), and
certificates verify that the server is who it claims to be.

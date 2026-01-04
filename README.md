# Network Security Project — 2024-2025 (short)

This repository contains four lab exercises. Implementations, tests and reports go in the `src` and `TraceRoute` folders.

- [Traceroute](#trace)
- [Server DNS Ad Blocker](#dns1)
- [ARP Spoofing](#arp)
- [TCP Hijacking](#tcp)

<a name="trace"></a>
## Traceroute
Implement a UDP-based traceroute, collect hop IPs and geolocate them. Produce a short route report.

<a name="dns1"></a>
## Server DNS Ad Blocker
Build a DNS resolver that blocks known ad/tracker domains (return 0.0.0.0) and logs blocked queries. Provide a docker-compose setup.

<a name="arp"></a>
## ARP Spoofing
Implement ARP cache poisoning in the lab environment to demonstrate a man-in-the-middle and packet forwarding.

<a name="tcp"></a>
## TCP Hijacking
Intercept and modify TCP payloads (e.g., via NFQueue/Scapy) to demonstrate session hijacking and payload injection.
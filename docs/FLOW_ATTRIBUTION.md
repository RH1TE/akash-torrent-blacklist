# Flow attribution and NAT

A complaint may report a public IP and an outbound source port that no Kubernetes Service or PodSpec lists. That is normal with network address translation.

## Addresses that must not be confused

1. Tenant address: on-chain `akash1...` wallet used to create a lease.
2. Pod address: private IP assigned by CNI, typically in a pod CIDR.
3. Service ClusterIP: virtual internal Kubernetes service address.
4. NodePort: external listening destination port for traffic arriving at a worker.
5. Public egress IP: source IPv4 after SNAT, sometimes shared by several pods and host VMs.
6. External peer address: remote endpoint observed by a complainant.
7. Source-port translation: ephemeral port chosen by conntrack or NAT, not generally listed as a Service port.

A complainant's `public-ip:42000` need not correspond to a pod's `containerPort` or `NodePort`.

## Evidence record

For reliable correlation, capture the following **at event time** in a restricted flow log, using a consistent timestamp format:

```json
{
  "at": "2026-01-15T12:00:00Z",
  "protocol": "tcp",
  "public_src_ip": "203.0.113.10",
  "public_src_port": 42000,
  "dest_ip": "198.51.100.40",
  "dest_port": 51413,
  "private_src_ip": "10.42.0.42",
  "private_src_port": 51922,
  "namespace": "tenant-namespace",
  "pod": "tenant-pod",
  "lease_dseq": "1792500000001",
  "observed_by": "worker-egress-sensor",
  "event_id": "flow-0001"
}
```

The sample addresses are documentation ranges. Source NAT mappings can expire very quickly. Keeping only ordinary ingress Nginx access logs or a daily firewall snapshot will not reconstruct them.

## Correlation rules

The offline correlator requires public IP, source port, protocol and time. The destination IP and destination port can optionally be supplied if the reporter provides them. Records with missing translation metadata, missing owner mapping, conflicting destinations, or multiple equally plausible sessions remain ambiguous.

The tool reports candidates and confidence based on matched recorded fields. It does not output a person's home IP. Unknown is a valid result, not a failure to be hidden.

## Recommended capture design

Record pod/namespace UID, deployment owner and DSEQ at observation time in a separate, access-controlled mapping store. Store start/end timestamps and short-lived source NAT connection records keyed by five-tuple. Ideally keep an event ID linking sensor and workload records. Restrict access to operators handling abuse and security reports. Prefer 7 to 14 days of flow metadata initially, with documented retention limits and incident holds.

Test privacy, volume and clock accuracy. Do not deploy packet payload capture by default. Traffic encrypted through a proxy or VPN may be attributable only to the tunnel endpoint and cannot prove the final content.

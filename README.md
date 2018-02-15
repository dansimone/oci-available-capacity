# OCI Available Capacity Tool 

This tool displays a summary of the available compute capacity in an OCI tenancy. 

## Prerequisites
- Install [Python](https://www.python.org/downloads) 2.7 or later.
- Install required Python packages:

```
pip install -r requirements.txt
```

- Details (OCID, private key, fingerprint) for a user in the "Auditors" or "Administrators" OCI group.

## Config File

Create a config file containing tenancy and user details in the "OCI" section, for example:

```
[OCI]
user: ocid1.user.oc1..aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
tenancy: ocid1.tenancy.oc1..aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
key_file: /tmp/my_api_key.pem
fingerprint: aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa
```

And sections for the service limits of each region: a list of compute shapes, and their capacities _per-AD_, for example:
 
```
[us-phoenix-1]
VM.Standard1.1: 5
VM.Standard1.2: 5
VM.Standard1.4: 5
VM.Standard1.8: 5

[us-ashburn-1]
VM.Standard1.1: 3
VM.Standard1.2: 2
VM.Standard1.4: 5
VM.Standard1.8: 1
```

Currently, these limits must be manually retrieved from the OCI Console: Region->Manage Regions->Service Limits.  Once
OCI exposes a REST API to retrieve these, this tool can be changed to use that, thus eliminating the need for the above 
sections of the config file. 

## Running the tool

```
python capacity.py --config /tmp/my_config
```

The output is something like this, showing the available capacity for each region/shape/AD:

```
************************************************
Available shapes in us-ashburn-1
************************************************
VM.Standard1.1: AD1: 3, AD2: 1, AD3: 1
VM.Standard1.2: AD1: 0, AD2: 1, AD3: 1
VM.Standard1.4: AD1: 5, AD2: 1, AD3: 4
VM.Standard1.8: AD1: 0, AD2: 0, AD3: 1
************************************************
Available shapes in us-phoenix-1
************************************************
VM.Standard1.1: AD1: 3, AD2: 1, AD3: 1
VM.Standard1.2: AD1: 0, AD2: 1, AD3: 2
VM.Standard1.4: AD1: 4, AD2: 2, AD3: 2
VM.Standard1.8: AD1: 0, AD2: 1, AD3: 1
```
import oci
import argparse
import ConfigParser

OCI_SECTION = 'OCI'

def get_available_capacity(config_file):

    # Parse config file for OCI credentials
    config = ConfigParser.ConfigParser()
    config.optionxform=str
    config.read(config_file)
    oci_config = {}
    oci_config["user"] = config.get(OCI_SECTION, 'user')
    oci_config["tenancy"] = config.get(OCI_SECTION, 'tenancy')
    oci_config["key_file"] = config.get(OCI_SECTION, 'key_file')
    oci_config["fingerprint"] = config.get(OCI_SECTION, 'fingerprint')

    available_capacity = {}

    # Parse available regions from config file
    regions = config.sections()
    regions.remove(OCI_SECTION)

    # Determine capacity per region
    for region in regions:
        # Connect to OCI for the region
        oci_config["region"] = region
        oci.config.validate_config(oci_config)
        cci = oci.core.compute_client.ComputeClient(oci_config)
        identity = oci.identity.IdentityClient(oci_config)

        # Initialize available capacity map for each provided shape, for each AD
        region_available_capacity = {}
        available_capacity[region] = region_available_capacity
        for (shape, number_per_ad) in config.items(region):
            int_per_ad = int(number_per_ad)
            region_available_capacity[shape] = [int_per_ad, int_per_ad, int_per_ad]

        # Loop through all compartments and count running compute instances
        for compartment in identity.list_compartments(compartment_id=oci_config['tenancy']).data:
            for instance in cci.list_instances(compartment_id=compartment.id).data:
                if instance.lifecycle_state == 'RUNNING' and instance.shape in region_available_capacity:
                    ad = int(instance.availability_domain.split('-')[-1])
                    region_available_capacity[instance.shape][ad - 1] -= 1
    return available_capacity

# Check parameters
parser = argparse.ArgumentParser(description='List available compute capacity in OCI')
parser.add_argument('--config', type=str, help='OCI config file')
args = parser.parse_args()

available_capacity = get_available_capacity(args.config)
for region in available_capacity:
    print '************************************************'
    print 'Available shapes in %s' % region
    print '************************************************'
    for shape in available_capacity[region]:
        ad_capacity_list = available_capacity[region][shape]
        if sum(ad_capacity_list) > 0:
            print '%s: AD1: %s, AD2: %s, AD3: %s' % (shape, ad_capacity_list[0], ad_capacity_list[1], ad_capacity_list[2])
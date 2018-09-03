import oci
import argparse
import ConfigParser

OCI_SECTION = 'OCI'

def get_region_availability_map(region, config, oci_config):
    """
    For the given region, returns a map of shape => available_per_ad_list
    """
    # Connect to OCI for the region
    oci_config["region"] = region
    oci.config.validate_config(oci_config)
    cci = oci.core.compute_client.ComputeClient(oci_config)
    identity = oci.identity.IdentityClient(oci_config)

    # Initialize available capacity map for each provided shape, for each AD
    region_availability_map = {}
    for (shape, capacity_per_ad) in config.items(region):
        int_per_ad = int(capacity_per_ad)
        region_availability_map[shape] = [int_per_ad, int_per_ad, int_per_ad]

    # Loop through all compartments and count running compute instances
    for compartment in identity.list_compartments(compartment_id=oci_config['tenancy']).data:
        for instance in cci.list_instances(compartment_id=compartment.id).data:
            if instance.lifecycle_state == 'RUNNING' and instance.shape in region_availability_map:
                ad = int(instance.availability_domain.split('-')[-1])
                region_availability_map[instance.shape][ad - 1] -= 1
    return region_availability_map

def get_total_availability_map(config_file):
    """
    Returns a map of region -> region_availability_map
    """
    # Parse config file for OCI credentials
    config = ConfigParser.ConfigParser()
    config.optionxform=str # makes case sensitive
    config.read(config_file)
    oci_config = {}
    oci_config["user"] = config.get(OCI_SECTION, 'user')
    oci_config["tenancy"] = config.get(OCI_SECTION, 'tenancy')
    oci_config["key_file"] = config.get(OCI_SECTION, 'key_file')
    oci_config["fingerprint"] = config.get(OCI_SECTION, 'fingerprint')

    # Parse available regions from config file
    regions = config.sections()
    regions.remove(OCI_SECTION)

    # Determine capacity per region
    total_availability_map = {}
    for region in regions:
        total_availability_map[region] = get_region_availability_map(region, config=config, oci_config=oci_config)
    return total_availability_map

if __name__ == "__main__":

    # Check parameters
    parser = argparse.ArgumentParser(description='List available compute capacity in OCI')
    parser.add_argument('--config', type=str, help='Config file', required=True)
    args = parser.parse_args()

    total_availability_map = get_total_availability_map(args.config)
    for region in total_availability_map:
        print '************************************************'
        print 'Available shapes in %s' % region
        print '************************************************'
        for shape in total_availability_map[region]:
            ad_capacity_list = total_availability_map[region][shape]
            print '%s: AD1: %s, AD2: %s, AD3: %s' % (shape, ad_capacity_list[0], ad_capacity_list[1], ad_capacity_list[2])

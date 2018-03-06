import argparse
import random
import sys
import compute_capacity

#
# Randomly chooses compute shapes based a set of "requests" and total available capacity.
# "Requests" are of the following form:
# "<request1_name>:<comma_separated_instances_per_ad> <request2_name:<comma_separated_instances_per_ad> ..."
# For example:
# "logging:2" will choose a shape for "logging" with 2 instances in one AD.
# "logging:2,1,3" will choose a shape for "logging" with 2 instances in one AD, 1 instance in another, and 3 in another.
#

def fulfill_compute_requests(region_availability_map, requests_map):
    """
    Given a region_availability_map and a set of compute requests (map of request_name => instances_per_ad_list),
    attempts to fulfill the requests for this region.  If successful, returns a map of
    request_name => (chosen_shape, chosen_ad_list).  Otherwise, returns None.
    """

    fulfillment_map = {}
    # Iterate over requests, in order of the most demaning requests first
    for (request_name, per_ad_request_list) in sorted(requests_map.iteritems(), key=lambda (k,v): max(v), reverse=True):
        # For this request, create a list of (candidate shape, candidate_ad_list) tuples that could fulfill the request
        # TODO - An improvement we can make is to sort the per_ad_request_list first, so that we check for the most demanding
        # AD request first
        candidates_list = []
        for shape in region_availability_map:

            # Make a copy of the shape's AD availability list, as we'll be modifying it while checking availability
            ad_availability_list = list(region_availability_map[shape])
            candidate_ad_list = []
            for ad_request in per_ad_request_list:

                # Determine ADs for this shape that could satisfy the AD request, ending the loop otherwise
                compatible_ad_list = [a for a in ad_availability_list if a >= ad_request]
                if len(compatible_ad_list) == 0:
                    break

                # For better randomization, randomly choose a compatible AD
                chose_ad_capacity = random.choice(compatible_ad_list)
                chosen_ad = random.choice([i for i, compatible_ad_list in enumerate(ad_availability_list) if compatible_ad_list == chose_ad_capacity])
                candidate_ad_list.append(chosen_ad)

                # Set the chosen AD's availability to 0 to prevent it from being chosen again for another AD of the same request
                ad_availability_list[chosen_ad] = 0

            # We have a candidate that satisfies all ADs of this request
            if len(candidate_ad_list) == len(per_ad_request_list):
                candidates_list.append((shape, candidate_ad_list))

        # Given the candidates we've collected, finally make a concrete selection for this request
        if len(candidates_list) > 0:
            (chosen_shape, chosen_ad_list) = random.choice(candidates_list)
            fulfillment_map[request_name] = (chosen_shape, chosen_ad_list)
            for index, ad_index in enumerate(chosen_ad_list):
                region_availability_map[chosen_shape][ad_index] -= per_ad_request_list[index]

    # If all requests fulfilled, return the full map
    if len(requests_map) == len(fulfillment_map):
        return fulfillment_map
    return None

if __name__ == "__main__":
    # Check parameters
    parser = argparse.ArgumentParser(description='List available compute capacity in OCI')
    parser.add_argument('--config', type=str, help='OCI availability config file', required=True)
    parser.add_argument('--requests', type=str, help='Space-separated list of requests to fulfill,'
                        + ' each of the form <request_name>:<comma_separated_instances_per_ad>', required=True)
    args = parser.parse_args()

    # Determine total availability
    total_availability_map = compute_capacity.get_total_availability_map(args.config)

    # Parse out the "requests map": a map of request_name -> [instances_per_ad_list]
    request_map = {}
    for request_string in args.requests.split():
        tokens = request_string.split(':')
        if len(tokens) != 2:
            raise Exception("Each request must be of the form <request_name>:<per_ad_request_list>")
        (request_name, per_ad_request_string) = tokens
        per_ad_request_list = per_ad_request_string.split(',')
        request_map[request_name] = list(map(int, per_ad_request_list))

    # Iterate over regions in random order, using the first region that fulfills all the given requests
    region_list = list(total_availability_map.keys())
    random.shuffle(region_list)
    for region in region_list:
        request_fullfillment = fulfill_compute_requests(total_availability_map[region], request_map)
        if request_fullfillment != None:
            print 'REGION=%s' % region
            for request_name in request_fullfillment:
                (shape, ad_list) = request_fullfillment[request_name]
                print '%s_SHAPE=%s' % (request_name.upper(), shape)
                for index, ad_index in enumerate(ad_list):
                    print '%s_AD%d=%d' % (request_name.upper(), index + 1, ad_index + 1)
                print '%s_ADS=%s' % (request_name.upper(), ','.join(str(x + 1) for x in ad_list))
            sys.exit(0)

    raise Exception('Out of capacity!')
from flask import Flask, request, Response
import geoip2.database
from dicttoxml import dicttoxml
import timeit
import os

app = Flask(__name__)

city_db_path = '/root/NINJA-IP-LOOKUP/ipdb/city.mmdb'
asn_db_path = '/root/NINJA-IP-LOOKUP/ipdb/asn.mmdb'

@app.route('/lookup', methods=['GET'])
def lookup_ip():
    ip_address = request.args.get('ip')

    if not ip_address:
        return generate_error_response('[NiNJA] IP Doesnt Exist!', 400)

    with geoip2.database.Reader(city_db_path) as city_reader, geoip2.database.Reader(asn_db_path) as asn_reader:
        try:
            start_time = timeit.default_timer()

            city_response = city_reader.city(ip_address)
            print(f"City: {city_response.city.name}")
            print(f"State: {city_response.subdivisions.most_specific.name}")
            print(f"Country: {city_response.country.name}")

            asn_response = asn_reader.asn(ip_address)
            print(f"ASN: {asn_response.autonomous_system_number}")
            print(f"ISP: {asn_response.autonomous_system_organization}")

            result = {
                'country': city_response.country.name if city_response.country.name else '',
                'state': city_response.subdivisions.most_specific.name if city_response.subdivisions.most_specific.name else '',
                'city': city_response.city.name if city_response.city.name else '',
                'asn': asn_response.autonomous_system_number,
                'isp': asn_response.autonomous_system_organization,
                'query': ip_address,
                '[NINJA]': 'Best Offhost Eva -- xor',
            }

            xml_content = dicttoxml(result, custom_root='query', attr_type=False)
            response_code = 200
            return Response(xml_content, content_type='application/xml', status=response_code)
        except geoip2.errors.AddressNotFoundError:
            return generate_error_response('[NiNJA] IP Address Not Found!', 404)

def generate_error_response(error_message, status_code):
    error_result = {'error': error_message, 'yikes': 'NiNJA Stealth'}
    xml_response = dicttoxml(error_result, custom_root='error', attr_type=False)
    return Response(xml_response, content_type='application/xml', status=status_code)

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=42069)

#!/usr/bin/env python
"""
Output yamllint result as checkstyle xml format.
"""

import sys
import subprocess
import xml.dom.minidom


def set_xml_attribute_from_dict(dom, xml_element, attribute_map):
    """
    Set attribuets of xml element from dictionary object
    """
    for name, value in attribute_map.items():
        attribute = dom.createAttribute(name)
        attribute.value = value
        xml_element.setAttributeNode(attribute)


def parse_yaml_result(yamllint_result):
    """
    Parse yaml result string
    """
    yamllint_file_info = yamllint_result.split(' ')[0]
    line_number = yamllint_file_info.split(':')[1]
    column_number = yamllint_file_info.split(':')[2]
    yamllint_severity_info = yamllint_result.split(' ')[1]
    severity = yamllint_severity_info[1:-1]
    message = ' '.join(yamllint_result.split(' ')[2:])
    return (line_number, column_number, severity, message)


def create_xml_element_for_file(dom, filename):
    """
    Create <file> element for the specified filename
    """
    xml_file = dom.createElement('file')
    set_xml_attribute_from_dict(dom, xml_file, {
        'name': filename
    })
    return xml_file


def main(file_names):
    """
    main entrypoint.
    """
    # checkstyle xml format is like
    # <checkstyle>
    #   <file name="foo/bar/baz.py">
    #         <error line='7' column='120' severity='info'
    #                message='Line is too long. [156/120]'
    #                source='com.puppycrawl.tools.checkstyle.Metrics/LineLength'/>
    #   </file>
    # </checkstyle>
    dom = xml.dom.minidom.Document()
    root = dom.createElement('checkstyle')
    dom.appendChild(root)
    for file_name in file_names:
        xml_file = create_xml_element_for_file(dom, file_name)
        root.appendChild(xml_file)
        commands = ['yamllint', file_name, '-f', 'parsable']
        try:
            yamllint_output = subprocess.check_output(commands)
        except subprocess.CalledProcessError as error:
            yamllint_output = error.output
        yamllint_result_array = yamllint_output.splitlines()
        for yamllint_result_bytes in yamllint_result_array:
            xml_error = dom.createElement('error')
            yaml_result = yamllint_result_bytes.decode('utf-8')
            (line_number, column_number, severity, message) = parse_yaml_result(yaml_result)
            set_xml_attribute_from_dict(dom, xml_error, {
                'line': line_number,
                'message': message,
                'column': column_number,
                'severity': severity
            })
            xml_file.appendChild(xml_error)
    print(dom.toprettyxml())


if __name__ == '__main__':
    main(sys.argv[1:])

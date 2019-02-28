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


def parse_cpplint_result(cpplint_result):
    """
    Parse cpplint result string
    """
    # cpplint_result is like:
    # sample_codes/hello_world.cpp:0: warning: No copyrigh ...
    cpplint_file_info = cpplint_result.split(' ')[0]
    line_number = cpplint_file_info.split(':')[1]
    column_number = '1'  # not specified
    severity = cpplint_result.split(':')[2].strip()
    message = ':'.join(cpplint_result.split(':')[3:])
    return {
        # cpplint line number starts with 0.
        'line': str(int(line_number) + 1),
        'column': column_number,
        'severity': severity,
        'message': message,
    }


def create_xml_element_for_file(dom, filename):
    """
    Create <file> element for the specified filename
    """
    xml_file = dom.createElement('file')
    set_xml_attribute_from_dict(dom, xml_file, {'name': filename})
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
        commands = ['cpplint', '--quiet', '--output', 'eclipse', file_name]
        try:
            cpplint_output = subprocess.check_output(
                commands, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as error:
            cpplint_output = error.output
        cpplint_result_array = cpplint_output.splitlines()
        for cpplint_result_bytes in cpplint_result_array:
            xml_error = dom.createElement('error')
            cpplint_result = cpplint_result_bytes.decode('utf-8')
            if cpplint_result.startswith(file_name):
                set_xml_attribute_from_dict(
                    dom, xml_error, parse_cpplint_result(cpplint_result))
                xml_file.appendChild(xml_error)
    print(dom.toprettyxml())


if __name__ == '__main__':
    main(sys.argv[1:])

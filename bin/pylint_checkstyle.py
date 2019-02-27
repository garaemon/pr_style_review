#!/usr/bin/env python

import json
import sys
import subprocess
import xml.dom.minidom


def set_xml_attribute_from_dict(dom, xml_element, attribute_map):
    for name, value in attribute_map.items():
        attribute = dom.createAttribute(name)
        attribute.value = value
        xml_element.setAttributeNode(attribute)


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
    for f in file_names:
        xml_file = dom.createElement('file')
        root.appendChild(xml_file)
        name_attribute = dom.createAttribute('name')
        name_attribute.value = f
        xml_file.setAttributeNode(name_attribute)
        commands = ['pylint', f, '-f', 'json']
        try:
            pylint_output = subprocess.check_output(commands)
        except Exception as e:
            pylint_output = e.output
        pylint_result_array = json.loads(pylint_output)
        for pylint_result in pylint_result_array:
            xml_error = dom.createElement('error')
            severity = pylint_result['type']
            if severity == 'convention':
                severity = 'info'
            set_xml_attribute_from_dict(dom, xml_error, {
                'line': str(pylint_result['line']),
                'messag': pylint_result['message'],
                'column': '1',
                'severity': severity
                # message-id
            })
            xml_file.appendChild(xml_error)
    print(dom.toprettyxml())


if __name__ == '__main__':
    main(sys.argv[1:])

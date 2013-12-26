#xml 小工具

###支持增删改查
###支持xpath定位节点

````
Usage: xl.py [options] -f arg1 -p arg2 -k arg3 [-v arg4]
        python xl.py -f xxx.xml -p .//db_node[@name='**']//db_user -k text
        python xl.py -f xxx.xml -p './/plugin[@lib='**']//hsmdb/table' -k name -v XXX
        python xl.py -f xxx.xml -p .//functions -a "<component dll='**' arg=''/>"
        

Options:
  -h, --help            show this help message and exit
  -f FILENAME           [must] file name of xml profile.
  -p XPATH              [must] xpath of xml profile to locate node U want to
                        handle.
  -k KEYWORD, --key=KEYWORD
                        [must] key, such as conn_count_upper_limit or text.
  -v VALUE, --value=VALUE
                        value, such as '50' or 'text'.
  -n                    output not sort.
  -a ADD_NODE, --append=ADD_NODE
                        append node.
````

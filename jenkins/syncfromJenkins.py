#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from time import sleep
import sys

URL = "http://10.2.99.100/jenkins/job/HS20_sync_serverfiles/api/python"
USERNAME = "cozhongkeshun"
PASSWORD = "cozhongkeshun123"
BUILD_UTL = "http://10.2.99.100/jenkins/job/HS20_sync_serverfiles/buildWithParameters"


def compile_python_api_code(content):
    p = compile(content, '', "eval")
    jenkins = eval(p)
    return jenkins

def url_visit(url, method='POST', pyapi=False, **params):
    try:
        req_params = {}
        req_params.update({'auth':(USERNAME, PASSWORD), 'verify':True})
        if params:
            req_params.update({'params': params})
        import requests
        def get_python_api_code(url, **params):
            response = requests.post(url, **params)
            return compile_python_api_code(response.content)

        if pyapi:
            jenkins = get_python_api_code(url, **req_params)
            return jenkins
        else:
            response = requests.post(url, **req_params)
            setattr(response, 'code', response.status_code)
            return response
    except ImportError:
        import base64, urllib2, urllib
        params.update({'username':USERNAME, 'password': PASSWORD, 'verify':True})
        base64str = base64.encodestring("%s:%s" % \
                (params['username'], params['password'])).replace('\n','')
        if pyapi:
            req = urllib2.Request(url)
            req.add_header("Authorization", "Basic %s" % base64str)
            content = urllib2.urlopen(req).read()
            return compile_python_api_code(content)
        else:
            gist_data = urllib.urlencode(params)
            req = urllib2.Request(url)
            req.add_header("Authorization", "Basic %s" % base64str)
            req.add_data(gist_data)
            response = urllib2.urlopen(req)
            return response


def main(uparams):
    params = {'SYSTEM': 'hs20',
              'DIR_DEST': '/home/hundsun/AUTO_UPDATE_DEPLOY',
              'HOST_DEST': '10.2.122.81'}
    if len(uparams) == 3:
        params = uparams
    bd_response = url_visit(BUILD_UTL, **params)
    if bd_response.code == '200':
        print 'Build Success .'
    print  "Waiting for 3s to allow Jenkins to catch up"
    _data = url_visit(URL, pyapi=True)
    total_wait = 0
    while _data['inQueue']:
         _data = url_visit(URL, pyapi=True)
         print "Waited %is for %s to begin..."%(total_wait,_data['displayName'])
         total_wait += 3
         sleep(3)
    curr_build = _data['lastBuild']['url'] + '/api/python'
    _build_data = url_visit(curr_build, pyapi=True)
    if _build_data['building']:
        running_build = _data['lastBuild']['number']
        count = 0
        delay = 3
        while _build_data['building']:
            _build_data = url_visit(curr_build, pyapi=True)
            total_wait = delay * count
            print "Waited %is for %s #%s to complete" % (total_wait, _data['displayName'], _data['name'])
            sleep(delay)
            count += 1

    print "Sync Complete for Success."


if __name__ == '__main__':
    params = {}
    print sys.argv
    if len(sys.argv) == 4:
        params.update({'SYSTEM': sys.argv[1],
                       'DIR_DEST': sys.argv[2],
                       'HOST_DEST': sys.argv[3]})
    else:
        print '''Usage: script_name [hs20/nxb] DIR_DEST HOST_DEST
        examples:
            python syncfromJenkins.py hs20 /home/hundsun/AUTO_UPDATE_DEPLOY 10.2.122.81

        if no parameters given, use default:
        'SYSTEM': 'hs20'
        'DIR_DEST': '/home/hundsun/AUTO_UPDATE_DEPLOY'
        'HOST_DEST': '10.2.122.81'
        '''
    main(params)


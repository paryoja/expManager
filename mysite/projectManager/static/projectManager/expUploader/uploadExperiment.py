#!/usr/bin/env python3

import json
import urllib.request
from datetime import datetime
from urllib.error import HTTPError

import requests


def urlJoin(urls):
    resultUrl = ''
    for url in urls:
        resultUrl = resultUrl + url.replace(' ', '%20')

        if not resultUrl.endswith('/'):
            resultUrl = resultUrl + '/'

    return resultUrl


class Setting:
    def __init__(self):

        # get project name
        with open('projectSetting.json') as setting:
            self.parsedSetting = json.loads(setting.read())
            self.projectName = self.parsedSetting['ProjectName']
            self.serverIp = self.parsedSetting['ServerIp']
            self.serverPort = self.parsedSetting['ServerPort']
            self.serverUrl = 'http://%s:%s/projects/' % (self.serverIp, self.serverPort)

            requestUrl = urlJoin([self.serverUrl, 'getProjectId/', self.projectName])
            with urllib.request.urlopen(requestUrl) as response:
                html = response.read().decode()
                self.projectId = html

            if self.projectId == '-1':
                print("Project does not exists. Check projectSetting.json or add a new project at the web site.")

            else:
                print("Project %s loaded (Id: %s)" % (self.projectName, self.projectId))

        self.client = requests.session()

    def post(self, post, fromUrl, toUrl, debug):
        getUrl = urlJoin([self.serverUrl, self.projectId, fromUrl])
        self.client.get(getUrl)

        csrftoken = self.client.cookies['csrftoken']

        Url = urlJoin([self.serverUrl, self.projectId, toUrl])
        post['csrfmiddlewaretoken'] = csrftoken
        r = self.client.post(Url, data=post, headers=dict(Referer=Url))

        if debug:
            with open('result.html', 'w') as w:
                w.write(r.text)

    def addDataset(self, dataset):
        fromUrl = 'datasetForm/'
        toUrl = 'addDataset/'

        post = {
            'name': dataset['name'],
            'is_synthetic': dataset['is_synthetic'],
        }
        if dataset['is_synthetic']:
            post['synthetic_parameters'] = json.dumps( dataset['synthetic_parameters'] )

        self.post(post, fromUrl, toUrl, False)

    def addAlgorithm(self, algorithm):
        fromUrl = 'algorithmForm/'
        toUrl = 'addAlgorithm/'

        post = {
            'name': algorithm['name'],
            'version': algorithm['version']
        }
        self.post(post, fromUrl, toUrl, False)

    def getObject(self, objectName, name):
        requestUrl = urlJoin([self.serverUrl, self.projectId, 'get' + objectName + 'Id', name])
        try:
            with urllib.request.urlopen(requestUrl) as response:
                return response.read().decode()
        except HTTPError:
            print(requestUrl)

    def addExperiment(self, dataset, algorithm, parameter, result):
        # check dataset exists
        datasetId = self.getObject('Dataset', dataset['name'])
        if datasetId == '-1':
            self.addDataset(dataset)
            datasetId = self.getObject('Dataset', dataset['name'])

        # check algorithm exists
        algorithmId = self.getObject('Algorithm', algorithm['name'])
        if algorithmId == '-1':
            self.addAlgorithm(algorithm)
            algorithmId = self.getObject('Algorithm', algorithm['name'])

        post = {'method': 'Add'}
        post['pub_date'] = datetime.now()
        post['parameter'] = parameter
        post['algorithm_name'] = algorithmId
        post['dataset_name'] = datasetId
        post['result'] = result

        self.post(post, 'expForm', 'addExp', False)

    def close(self):
        self.client.close()

import sys
import os
if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("There is no input argument")
        sys.exit(1) 

    method = sys.argv[1]

    setting = Setting()
    if method == 'dataset':
        print( 'Adding a new dataset' )

        dataset = {}
        dataset['name'] = sys.argv[2]
        dataset['is_synthetic'] = sys.argv[3]
        dataset['synthetic_parameters'] = sys.argv[4]

        datasetId = setting.getObject('Dataset', dataset['name'])
        if datasetId == '-1':
            setting.addDataset(dataset)

    elif method == 'algorithm':
        print( 'Adding a new algorithm' )

        algorithm = {}
        algorithm['name'] = sys.argv[2]
        algorithm['version'] = sys.argv[3]

        algorithmId = setting.getObject('Algorithm', algorithm['name'])
        if algorithmId == '-1':
            setting.addAlgorithm(algorithm)


    elif method == 'exp':
        print( 'Adding a new experiment' )
        for fileName in os.listdir( 'json' ):
            if fileName.endswith('.txt'):
                with open( os.path.join( 'json', fileName ) ) as r:
                    for line in r:
                        parsed = json.loads(line)

                        algorithm = parsed[ 'Algorithm' ]
                        dataset = parsed[ 'Dataset' ]
                        parameter = json.dumps( parsed[ 'ParametersUsed' ] )
                        result = json.dumps( parsed[ 'Result' ] )

                        setting.addExperiment( dataset, algorithm, parameter, result )
                # move file
                #os.remove( os.path.join( 'json', fileName ) )
                os.rename( os.path.join( 'json', fileName ), os.path.join( 'json', 'uploaded', fileName ) )

    setting.close()

    #algorithm = {
    #    'name': 'MYALGO',
    #    'version': '0.1'
    #}

    #parameter = '{ "threshold" : "0.1" }'
    #result = '{ "executionTime" : "100", "buildTime" : "10" }'

    #setting.addExperiment(dataset, algorithm, parameter, result)

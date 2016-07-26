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

    def addDataset(self, name, is_synthetic, synthetic_parameters):
        fromUrl = 'datasetForm/'
        toUrl = 'addDataset/'

        post = {
            'name': name,
            'is_synthetic': is_synthetic,
        }
        if is_synthetic:
            post['synthetic_parameters'] = synthetic_parameters

        self.post(post, fromUrl, toUrl, False)

    def addAlgorithm(self, name, version):
        fromUrl = 'algorithmForm/'
        toUrl = 'addAlgorithm/'

        post = {
            'name': name,
            'version': version
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
            self.addDataset(dataset['name'], dataset['is_synthetic'], dataset['synthetic_parameters'])
            datasetId = self.getObject('Dataset', dataset['name'])

        # check algorithm exists
        algorithmId = self.getObject('Algorithm', algorithm['name'])
        if algorithmId == '-1':
            self.addAlgorithm(algorithm['name'], algorithm['version'])
            algorithmId = self.getObject('Algorithm', algorithm['name'])

        post = {'method': 'Add'}
        post['pub_date'] = datetime.now()
        post['parameter'] = parameter
        post['algorithm_name'] = algorithmId
        post['dataset_name'] = datasetId
        post['result'] = result

        self.post(post, 'expForm', 'addExp', False)


setting = Setting()

dataset = {
    'name': 'synth',
    'is_synthetic': 'True',
    'synthetic_parameters': '{ "datasize" : "1000", "dimension" : "6"  }'
}

algorithm = {
    'name': 'MYALGO',
    'version': '0.1'
}

parameter = '{ "threshold" : "0.1" }'
result = '{ "executionTime" : "100", "buildTime" : "10" }'

setting.addExperiment(dataset, algorithm, parameter, result)

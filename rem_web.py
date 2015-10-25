# -*- coding: utf-8 -*-
"""
Created on Sat Aug 29 12:21:36 2015

@author: jakoberickson
"""
from datetime import datetime
import urllib
import re
from lxml import html

ZWSID = 'zws-id=' + 'X1-ZWz1evxmk11c7f_9abc1'
webpage = 'http://www.zillow.com/webservice/GetDeepSearchResults.htm'
base_url = '?'.join([webpage, ZWSID])
COM_labels =[
'Bedrooms',
'Building Area(+ Basement)',
'Year Built',
'Stories',
'Baths',
'Finished Basement',
'Second Floor',
'Basement Area',
'Ground Floor',
'Residence Rooms',
'Stories',
'Reference Dwellings',
'Building Code',
'Establishments',
'LotSize']


urlheader1 = 'http://apps.ci.minneapolis.mn.us/PIApp/ValuationRpt.aspx?pid='
urlheader2 = ('http://apps.ci.minneapolis.mn.us/PIApp/StructureInformationRpt.'
              'aspx?pid=')
urlheader3 = 'http://apps.ci.minneapolis.mn.us/PIApp/GeneralInfoRpt.aspx?pid='


class WebScraper():
    def __init__(self, propertyID):
        self.propertyID = propertyID
        url = urlheader1 + format(self.propertyID, '013')
        print 'getting web data',
        self.access_web(url)
        try:
            self._validate_ID()
            self.get_house()
            self.get_citystatezip()
            self.address = [self.house] + self.citystatezip.replace(',', '').split() + ['']
        except:
            self.address = []
        try:
            self.get_salesdata()
        except:
            self.salesdata = []
        print '.',
        tempurl = urlheader2 + format(self.propertyID, '013')
        url = self._get_structure(tempurl)
        print '.',
        self.access_web(url)
        try:
            self._validate_ID()
            self._get_detailed_info()
        except:
            self.info = {}
        print '.',
        url = urlheader3 + format(self.propertyID, '013')
        self.access_web(url)
        try:
            self._validate_ID()
            self._get_general_info()
        except:
            pass
        self.info = self._integerize(self.info)


    def _get_structure(self, url):
        f = urllib.urlopen(url)
        contents = f.read()
        f.close()
        pattern = re.findall('Structure=[1-9]+', contents)[0]
        return urlheader2 + '&'.join([format(self.propertyID, '013'),
                                      pattern,
                                      'Action=Show'])

    def access_web(self, url):
        f = urllib.urlopen(url)
        contents = f.read()
        f.close()
        self.tree = html.fromstring(contents)


    def _validate_ID(self):
        if 'Oops!' in self.tree.xpath('//h3/text()'):
            self.valid_id = False
            raise Exception
        if self.tree.xpath('//p[@class="noResultsMsg"]/text()'):
            self.valid_id = False
            raise Exception
        else:
            self.valid_id = True


    def get_house(self):
        self.house =  ' '.join(self.tree.xpath('//span/text()')[1:])


    def get_citystatezip(self):
        self.citystatezip = [str(item.strip()) for item in 
                self.tree.xpath('//td[@colspan="2"]/text()')][0]


    def _get_general_info(self):
        xpath = '//table[@class="section float"]/tr//*/text()'
        rawdata = self.tree.xpath(xpath)
        starting_index = rawdata.index('Lot Size')
        sliced = rawdata[starting_index:starting_index+4]
        cleandata = [re.sub('[ \\r\\n]', '', item) for item in sliced]
        for i in range(0, 4, 2):
            self.info[cleandata[i]] = cleandata[i+1]



    def get_salesdata(self):
        rawsales = self.tree.xpath('//table[@class="rtable"]/tr/td/text()')
        if any('No sales history' in _ for _ in rawsales):
            self.salesdata =  []
        self.salesdata = self.clean_salesdata(rawsales[1:])
        return


    def clean_salesdata(self, rawsales):
        raw_dates = [rawsales[i] for i in range(0, len(rawsales), 4)]
        date_strings = [self.format_date(date) for date in raw_dates]
        raw_prices = [rawsales[i+3] for i in range(0, len(rawsales), 4)]
        integer_prices = [int(re.sub('[$,]', '', item)) for item in raw_prices]
        return zip(date_strings, integer_prices)


    def _get_detailed_info(self):
        
        xpath = '//table[@class="rtable"]//*/text()'
        data = [_.strip(':') for _ in self.tree.xpath(xpath) if _.strip()][1:]
        self.info = {data[i]:data[i+1] for i in range(0, len(data), 2)}


    def _integerize(self, data):
        for key in data.keys():
            try:
                data[key] = int(re.sub('[$,]', '', data[key]))
            except:
                try:
                    data[key] = float(re.sub('[$,]', '', data[key]))
                except:
                    pass
        return data


    def format_date(self, date_string):
        temp = datetime.strptime(date_string, '%b %d, %Y')
        return datetime.strftime(temp, '%Y-%m-%d')


#def get_data_from_web2(propertyID):
#    pass
#
#def get_data_from_web(address):
#    house, city, state, _, _ = address
#    house = 'address=' + '+'.join(house.split(' '))
#    citystatezip = 'citystatezip=' + city.strip() + '%2C' + state.strip()
#    url = '&'.join([base_url, house, citystatezip])
#    url = str(url)
#
#    f = urllib.urlopen(url)
#    contents = f.read()
#    f.close()
#
#
#    root = etree.fromstring(contents)
#    code = root.xpath('//code')[0].text
#    if int(code) == 0:
#        results = {}
#        for element in root.iter():
#            if element.tag.lower() in zillowlabels:
#                results[element.tag.lower()] = element.text
#        return results
#    else:
#        raise Exception(code)

#class ZillowError(Exception):
#    def __init__(self, value):
#       self.value = value
#    def __str__(self):
#       return 'Zillow Error Code: {}'.format(self.value)





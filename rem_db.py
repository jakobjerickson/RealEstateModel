# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 11:24:48 2015

@author: jakoberickson
"""

import sqlite3
import rem_web


address_cols = {
'bathrooms': 'Bath',
'bedrooms': 'Bdrm',
'finishedsqft': 'Sqft',
'lotsizesqft': 'LotSize',
'totalrooms': 'TotalRooms',
'usecode': 'Type',
'yearbuilt': 'YearBuilt'}


address_cols2 = {
'Bedrooms': 'Bdrm',
'Year Built': 'YearBuilt',
'Building Code': 'Type',
'Baths': 'Bath',
'Residence Rooms': 'TotalRooms',
'Ground Floor': 'GrndFloor',
'Second Floor': 'SecondFloor',
}


column_labels ={
'Bedrooms': 'Bdrm',
'Building Area(+ Basement)': 'TotalSqFt',
'Year Built': 'YearBuilt',
'Baths': 'Bath',
'Finished Basement': 'FnshdBsmntSqFt',
'Second Floor': 'ScndSqFt',
'Basement Area': 'BsmntSqFt',
'Ground Floor': 'GrndSqFt',
'Residence Rooms': 'TotalRooms',
'Stories': 'Stories',
'Building Code': 'Type',
'LotSize': 'LotSize',
'Tract/Block': 'TractBlock'}


sales_cols = {
'lastsolddate': 'Closed',
'lastsoldprice': 'SoldFor',
}


class remDB():
    def __init__(self, filename):
        self.filename = filename
        self.table = 'PropertyDetails'
        self.sales_table = 'SalesHistory'
        self.db = sqlite3.connect(self.filename)
        self.db.row_factory = sqlite3.Row
        self.db.execute('''CREATE TABLE IF NOT EXISTS {}(
                           ID               INTEGER PRIMARY KEY,
                           PropID           INTEGER,
                           Address          TEXT,
                           City             TEXT,
                           State            TEXT,
                           Zip              TEXT,
                           ZipExt           TEXT,
                           TractBlock       TEXT,
                           Type             TEXT,
                           YearBuilt        INTEGER,
                           Stories          FLOAT,
                           Bdrm             INTEGER,
                           Bath             INTEGER,
                           TotalRooms       INTEGER,
                           TotalSqft        INTEGER,
                           GrndSqFt         INTEGER,
                           ScndSqFt         INTEGER,
                           BsmntSqFt        INTEGER,
                           FnshdBsmntSqFt   INTEGER,
                           LotSize          INTEGER,
                           Garage           INTEGER,
                           Status           TEXT)'''
                               .format(self.table))
        self.db.execute('''CREATE TABLE IF NOT EXISTS {}(
                        SalesID        INTEGER PRIMARY KEY,
                        AddressID      INTEGER,
                        Date            TEXT,
                        Price           INTEGER,
                        FOREIGN KEY (AddressID) REFERENCES Address(ID))'''
                        .format(self.sales_table))


    def __iter__(self):
        pass


    def get_details_for_address(self, address):
        """
        Given an address, returns a dictionary 
        NOTE: address must be properly formatted "House Number, Street, City,
        2-digitTstate, XXXXX or XXXXX-XXXX Zip"
        NOTE: updates the database first!
        """
        print 'checking database for' + ' '.join(address)
        try:
            address = house, city, state, zipcode = address.split(', ')
            try:
                address[3:5] = zipcode.split('-')
            except ValueError:
                address.append('')
        except ValueError:
            address = address.split(', ') + [''] * 2
        status_check = self._check_status_for_address(address)
        try:
            status = status_check['STATUS']
        except:
            print 'adding address...'
            self._add_address(address)
            status_check = self._check_status_for_address(address)
        status = status_check['Status']
        ID = status_check['ID']
        if status == 'PARTIAL':
            print 'updating address...'
            self._update_details_for_address(address, ID)
            status = self._check_status_for_address(address)['STATUS']
        if status == 'COMPLETE':
            self.db.execute('''SELECT * FROM {table}
                            WHERE ID = "{ID}"'''.format(table = self.table,
                                                           ID = ID))


    def get_details_for_PropID(self, PropID):
        """
        Given a PropID for the ciy of minneapolis properties webiste, returns
        a dictionary with the status of PropID in the database.
        NOTE: updates the database first!
        """
        status_check = self._check_status_for_PropID(PropID)
        try:
            status = status_check['Status']
        except TypeError:
            print 'adding {}'.format(PropID)
            self._add_PropID(PropID)
            status_check = self._check_status_for_PropID(PropID)
        status = status_check['Status']
        if status == 'INVALID':
            return 'Invalid PropID'
#        if status == 'PARTIAL':
#            self._update_details_address(ID)
#            status = self._check_status_for_PropID(PropID)['STATUS']
        if status == 'COMPLETE':
            cursor = self.db.execute('''SELECT * FROM {table}
                            WHERE PropID = "{PropID}"'''.format(
                                table = self.table,
                                PropID = PropID))
            for row in cursor:
                return dict(row)


    def _check_status_for_PropID(self, PropID):
        """
        Internal method that returns a dictionary with the ID and Status
        for the given address
        """
        cursor = self.db.execute('''SELECT ID, Status FROM {table}
                                 WHERE (PropID = {PropID})'''.format(
                                     table = self.table,
                                     PropID = PropID))
        for row in cursor:
            return dict(row)


    def _check_status_for_address(self, address):
        """
        Internal method that returns a dictionary with the ID and Status
        for the given address
        """
        house, city, state, zip5, zip4 = address
        cursor = self.db.execute('''SELECT ID, Status FROM {table}
                                 WHERE (Address = "{house}" AND
                                 City = "{city}" AND
                                 State = "{state}")'''.format(
                                     table = self.table,
                                     house = house,
                                     city = city,
                                     state = state))
        for row in cursor:
            return dict(row)


    def _add_address(self, address, PropID = None):
        house, city, state, zip5, zip4 = address
        if not PropID:
            self.db.execute('''INSERT INTO {table} 
                            (Address, City, State, Zip, ZipExt, Status)
                            VALUES ("{house}", "{city}", "{state}", "{zip5}",
                            "{zip4}","PARTIAL")'''.format(table = self.table,
                                                          house = house,
                                                          city = city,
                                                          state = state,
                                                          zip5 = zip5,
                                                          zip4 = zip4))
        else:
            self.db.execute('''INSERT INTO {table} 
                            (Address, City, State, Zip, ZipExt, Status, PropID)
                            VALUES ("{house}", "{city}", "{state}", "{zip5}",
                            "{zip4}","PARTIAL", {PropID})'''.format(
                                table = self.table,
                                house = house,
                                city = city,
                                state = state,
                                zip5 = zip5,
                                zip4 = zip4,
                                PropID = PropID))
        self.db.commit()
        return


    def _add_PropID(self, PropID):
        try:
            web_data= rem_web.WebScraper(PropID)
        except:
            self.db.execute('''INSERT INTO {table} (PropID, Status) 
                            VALUES ({PropID}, "INVALID")'''.format(
                                table=self.table,
                                PropID = PropID))
            return
        self._add_address(web_data.address, PropID)
        status = self._check_status_for_address(web_data.address)
        try:
            ID = status['ID']
        except:
            raise Exception('Error adding address!')
        self._update_details_for_address(ID, web_data.info)
        self._update_sales_data(ID, web_data.salesdata)
        return


    def _update_details_for_address(self, ID, info):
        for key in column_labels:
            try:
                self.db.execute('''UPDATE {table} SET {col} = {value} WHERE
                                ID = {ID}'''.format(table = self.table,
                                                     col = column_labels[key],
                                                     value = info[key],
                                                     ID = ID))
            except sqlite3.OperationalError:
                self.db.execute('''UPDATE {table} SET {col} = "{value}" WHERE
                                ID = {ID}'''.format(table = self.table,
                                                     col = column_labels[key],
                                                     value = info[key],
                                                     ID = ID))
            except:
                pass
#            print '''UPDATE {table} SET {col} = {value} WHERE
#                            ID = {ID}'''.format(table = self.table,
#                                                 col = address_cols[key],
#                                                 value = value,
#                                                 ID = ID)
        self.db.execute('''UPDATE {table} SET Status = "COMPLETE"
                        WHERE ID = {ID}'''.format(table = self.table, ID = ID))
        self.db.commit()
#        self._update_sales_data(ID, web_data)
        return


#    def update_address(self, scraper):
#        address = scraper.address
#        status_check = self._check_status_for_address(address)
#        try:
#            status = status_check['STATUS']
#        except:
#            self._add_address(address)
#            status_check = self._check_status_for_address(address)
#        status = status_check['Status']
#        ID = status_check['ID']
#        self.db.execute('''UPDATE {table} SET ''')



    def _update_sales_data(self, ID,sales_data):
        print 'updating sales data!'
        print sales_data
        for row in sales_data:
            if not self._check_sales_status(ID, row):
                self.db.execute('''INSERT INTO {table}
                                (AddressID, Price, Date)
                                VALUES ({ID}, {price}, "{date}")'''
                                    .format(
                                    table = self.sales_table,
                                    ID = ID,
                                    price = row[1],
                                    date = row[0]))
            self.db.commit()
        return


    def _check_sales_status(self, ID, web_data):
        print web_data
        cursor = self.db.execute('''SELECT SalesID FROM {table} WHERE (
                                    AddressID = {ID} AND
                                    Price = {price} AND
                                    Date = "{date}")'''
                                    .format(
                                         table = self.sales_table,
                                         ID = ID,
                                         price = web_data[1],
                                         date = web_data[0]))
        for row in cursor:
            return dict(row)


    def close(self):
        self.db.close()
        return

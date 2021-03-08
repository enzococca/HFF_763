#! /usr/bin/env python
# -*- coding: utf 8 -*-
"""
/***************************************************************************
        HFF_system Plugin  - A QGIS plugin to manage archaeological dataset
                             stored in Postgres
                             -------------------
    begin                : 2020-01-01
    copyright            : (C) 2008 by Enzo Cocca
    email                : enzo.ccc at gmail.com
 ***************************************************************************/
/***************************************************************************
 *                                                                          *
 *   This program is free software; you can redistribute it and/or modify   *
 *   it under the terms of the GNU General Public License as published by   *
 *   the Free Software Foundation; either version 2 of the License, or      *
 *   (at your option) any later version.                                    *                                                                       *
 ***************************************************************************/
"""
from __future__ import absolute_import
import os
from datetime import date
import sqlite3 as sq
import subprocess
import sys
import pandas as pd
import numpy as np
import time
import platform
from builtins import range
from builtins import str
from qgis.PyQt.QtGui import QDesktopServices,QColor, QIcon,QStandardItemModel
from qgis.PyQt.QtCore import QUrl, QVariant,Qt, QSize,QPersistentModelIndex
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QListWidget, QListView, QFrame, QAbstractItemView,QFileDialog, QTableWidgetItem, QListWidgetItem
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsSettings
from ..modules.utility.hff_system__OS_utility import Hff_OS_Utility
from ..modules.db.hff_system__conn_strings import Connection
from ..modules.db.hff_db_manager import Hff_db_management
from ..modules.db.hff_system__utility import Utility
from ..modules.gis.hff_system__pyqgis import Hff_pyqgis
from ..modules.utility.print_relazione_pdf import exp_rel_pdf
from ..modules.utility.hff_system__error_check import Error_check
from ..modules.utility.delegateComboBox import ComboBoxDelegate
from ..test_area import Test_area
from ..gui.imageViewer import ImageViewer
from ..gui.sortpanelmain import SortPanelMain
from ..modules.utility.settings import Settings
from .Excel_export import hff_system__excel_export
from qgis.gui import QgsMapCanvas, QgsMapToolPan
from ..modules.utility.hff_system__exp_site_pdf import *
import openpyxl
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Alignment
from openpyxl.workbook import Workbook 
from sqlalchemy import create_engine
MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), os.pardir, 'gui', 'ui', 'Eamena.ui'))
class Eamena(QDialog, MAIN_DIALOG_CLASS):
    """This class provides to manage the Site Sheet"""
    MSG_BOX_TITLE = "HFF system - Eamena form"
    DATA_LIST = []
    DATA_LIST_REC_CORR = []
    DATA_LIST_REC_TEMP = []
    REC_CORR = 0
    REC_TOT = 0
    STATUS_ITEMS = {"b": "Current", "f": "Find", "n": "New Record"}
    BROWSE_STATUS = "b"
    SORT_MODE = 'asc'
    SORTED_ITEMS = {"n": "Not sorted", "o": "Sorted"}
    SORT_STATUS = "n"
    UTILITY = Utility()
    DB_MANAGER = ""
    TABLE_NAME = 'eamena_table'
    MAPPER_TABLE_CLASS = "EAMENA"
    NOME_SCHEDA = "Eamena Form"
    ID_TABLE = "id_eamena"
    CONVERSION_DICT = {
        ID_TABLE: ID_TABLE,
        "Location":" location",
        "assessment_investigator_actor":"assessment_investigator_actor",
        "investigator_role_type":"investigator_role_type",
        "assessment_activity_type":"assessment_activity_type",
        "assessment_activity_date":"assessment_activity_date",
        "ge_assessment":"ge_assessment",
        "ge_imagery_acquisition_date":"ge_imagery_acquisition_dat",
        "information_resource_used":"information_resource_used",
        "information_resource_acquisition_date":"information_resource_acquisition_date",
        "Resource Name":"resource_name",
        "name_type":"name_type",
        "Heritage place type":"heritage_place_type",
        "general_description_type":"general_description_type",
        "general_description":"general_description",
        "heritage_place_function":"heritage_place_function",
        "heritage_place_function_certainty":"heritage_place_function_certainty",
        "designation":"designation",
        "designation_from_date":"designation_from_date",
        "designation_to_date":"designation_to_date",
        "geometric_place_expression":"geometric_place_expression",
        "geometry_qualifier":"geometry_qualifier",
        "site_location_certainty":"site_location_certainty",
        "geometry_extent_certainty":"geometry_extent_certainty",
        "site_overall_shape_type":"site_overall_shape_type",
        "Grid":"grid_id",
        "country_type":"country_type",
        "cadastral_reference":"cadastral_reference",
        "resource_orientation":"resource_orientation",
        "address":"address",
        "address_type":"address_type",
        "administrative_subdivision":"administrative_subdivision",
        "administrative_subdivision_type":"administrative_subdivision_type",
        "overall_archaeological_certainty_value":"overall_archaeological_certainty_value",
        "overall_site_morphology_type":"overall_site_morphology_type",
        "cultural_period_type":"cultural_period_type",
        "cultural_period_certainty":"cultural_period_certainty",
        "cultural_subperiod_type":"cultural_subperiod_type",
        "cultural_subperiod_certainty":"cultural_subperiod_certainty",
        "date_inference_making_actor":"date_inference_making_actor",
        "archaeological_date_from":"archaeological_date_from",
        "archaeological_date_to":"archaeological_date_to",
        "bp_date_from":"bp_date_from",
        "bp_date_to":"bp_date_to",
        "ah_date_from":"ah_date_from",
        "ah_date_to":"ah_date_tov",
        "sh_date_from":"sh_date_from",
        "sh_date_to":"sh_date_to",
        "site_feature_form_type":"site_feature_form_typ",
        "site_feature_form_type_certainty":"site_feature_form_type_certainty",
        "site_feature_shape_type":"site_feature_shape_type",
        "site_feature_arrangement_type":"site_feature_arrangement_type",
        "site_feature_number_type":"site_feature_number_type",
        "site_feature_interpretation_type":"site_feature_interpretation_type",
        "site_feature_interpretation_number":"site_feature_interpretation_number",
        "site_feature_interpretation_certainty":"site_feature_interpretation_certainty",
        "built_component_related_resource":"built_component_related_resource",
        "hp_related_resource":"hp_related_resource",
        "material_class":"material_class",
        "material_type":"material_type",
        "construction_technique":"construction_technique",
        "measurement_number":"measurement_number",
        "measurement_unit":"measurement_unit",
        "dimension_type":"dimension_type",
        "measurement_source_type":"measurement_source_type",
        "related_geoarch_palaeo":"related_geoarch_palaeo",
        "overall_condition_state":"overall_condition_state",
        "damage_extent_type":"damage_extent_type",
        "disturbance_cause_category_type":"disturbance_cause_category_type",
        "disturbance_cause_type":"disturbance_cause_type",
        "disturbance_cause_certainty":"disturbance_cause_certainty",
        "disturbance_date_from":"disturbance_date_from",
        "disturbance_date_to":"disturbance_date_to",
        "disturbance_date_occurred_before":"disturbance_date_occurred_before",
        "disturbance_date_occurred_on":"disturbance_date_occurred_on",
        "disturbance_cause_assignment_assessor_name":"disturbance_cause_assignment_assessor_name",
        "effect_type":"effect_type",
        "effect_certainty":"effect_certainty",
        "threat_category":"threat_category",
        "threat_type":"threat_type",
        "threat_probability":"hreat_probability",
        "threat_inference_making_assessor_name":"threat_inference_making_assessor_name",
        "intervention_activity_type":"intervention_activity_type",
        "recommendation_type":"recommendation_type",
        "priority_type":"priority_typ",
        "related_detailed_condition_resource":"related_detailed_condition_resource",
        "topography_type":"topography_type",
        "land_cover_type":"land_cover_type",
        "land_cover_assessment_date":"land_cover_assessment_date",
        "surficial_geology_type":"surficial_geology_type",
        "depositional_process":"depositional_process",
        "bedrock_geology":"bedrock_geology",
        "fetch_type":"fetch_type",
        "wave_climate":"wave_climate",
        "tidal_energy":"tidal_energy",
        "minimum_depth_max_elevation":"minimum_depth_max_elevation",
        "maximum_depth_min_elevation":"maximum_depth_min_elevation",
        "datum_type":"datum_type",
        "datum_description_epsg_code":"datum_description_epsg_code",
        "restricted_access_record_designation":"restricted_access_record_designation",
    }
    SORT_ITEMS = [
        ID_TABLE,
        "Location", 
        "Resource Name", 
        "Grid", 
        "Heritage place type"
    ]
    TABLE_FIELDS = [
        "location",
        "assessment_investigator_actor",
        "investigator_role_type",
        "assessment_activity_type",
        "assessment_activity_date",
        "ge_assessment",
        "ge_imagery_acquisition_date",
        "information_resource_used",
        "information_resource_acquisition_date",
        "resource_name",
        "name_type",
        "heritage_place_type",
        "general_description_type",
        "general_description",
        "heritage_place_function",
        "heritage_place_function_certainty",
        "designation",
        "designation_from_date",
        "designation_to_date",
        "geometric_place_expression",
        "geometry_qualifier",
        "site_location_certainty",
        "geometry_extent_certainty",
        "site_overall_shape_type",
        "grid_id",
        "country_type",
        "cadastral_reference",
        "resource_orientation",
        "address",
        "address_type",
        "administrative_subdivision",
        "administrative_subdivision_type",
        "overall_archaeological_certainty_value",
        "overall_site_morphology_type",
        "cultural_period_type",
        "cultural_period_certainty",
        "cultural_subperiod_type",
        "cultural_subperiod_certainty",
        "date_inference_making_actor",
        "archaeological_date_from",
        "archaeological_date_to",
        "bp_date_from",
        "bp_date_to",
        "ah_date_from",
        "ah_date_to",
        "sh_date_from",
        "sh_date_to",
        "site_feature_form_type",
        "site_feature_form_type_certainty",
        "site_feature_shape_type",
        "site_feature_arrangement_type",
        "site_feature_number_type",
        "site_feature_interpretation_type",
        "site_feature_interpretation_number",
        "site_feature_interpretation_certainty",
        "built_component_related_resource",
        "hp_related_resource",
        "material_class",
        "material_type",
        "construction_technique",
        "measurement_number",
        "measurement_unit",
        "dimension_type",
        "measurement_source_type",
        "related_geoarch_palaeo",
        "overall_condition_state",
        "damage_extent_type",
        "disturbance_cause_category_type",
        "disturbance_cause_type",
        "disturbance_cause_certainty",
        "disturbance_date_from",
        "disturbance_date_to",
        "disturbance_date_occurred_before",
        "disturbance_date_occurred_on",
        "disturbance_cause_assignment_assessor_name",
        "effect_type",
        "effect_certainty",
        "threat_category",
        "threat_type",
        "threat_probability",
        "threat_inference_making_assessor_name",
        "intervention_activity_type",
        "recommendation_type",
        "priority_type",
        "related_detailed_condition_resource",
        "topography_type",
        "land_cover_type",
        "land_cover_assessment_date",
        "surficial_geology_type",
        "depositional_process",
        "bedrock_geology",
        "fetch_type",
        "wave_climate",
        "tidal_energy",
        "minimum_depth_max_elevation",
        "maximum_depth_min_elevation",
        "datum_type",
        "datum_description_epsg_code",
        "restricted_access_record_designation",
    ]
    DB_SERVER = "not defined"  ####nuovo sistema sort
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.pyQGIS = Hff_pyqgis(iface)
        self.setupUi(self)
        self.currentLayerId = None
        self.HOME = os.environ['HFF_HOME']
        try:
            self.on_pushButton_connect_pressed()
        except Exception as e:
            QMessageBox.warning(self, "Connection system", str(e), QMessageBox.Ok)
        sito = self.comboBox_name_site.currentText()
        self.comboBox_name_site.setEditText(sito)
        self.empty_fields()
        self.fill_fields()
        self.model = QStandardItemModel()
        self.customize_GUI()
        if len(self.DATA_LIST)==0:
            self.comboBox_name_site.setCurrentIndex(0)
        else:
            self.comboBox_name_site.setCurrentIndex(1)
        self.comboBox_name_site.currentIndexChanged.connect(self.geometry_exp)
    def geometry_exp(self):
        
        self.tableWidget_geometry_place.update()
        search_dict = {
            'location': "'" + str(self.comboBox_location.currentText()) + "'",
            'name_feat': "'" + str(self.comboBox_name_site.currentText()) + "'"
        }
    
        geometry_vl = self.DB_MANAGER.query_bool(search_dict,'SITE_POLYGON')
        geometry_list = []
        
        for i in range(len(geometry_vl)):
            geometry_list.append(str(geometry_vl[i].coord))
        
        search_dict1 = {
            'location': "'" + str(self.comboBox_location.currentText()) + "'",
            'name_f_l': "'" + str(self.comboBox_name_site.currentText()) + "'"
        }
    
        geometry_vl_1 = self.DB_MANAGER.query_bool(search_dict1,'SITE_LINE')
        geometry_list_1 = []
        for a in range(len(geometry_vl_1)):
            geometry_list_1.append(str(geometry_vl_1[a].coord))
            # geometry_list.append(str(geometry_vl[a].coord))
        
        a=geometry_list+geometry_list_1
        # geometry_place= self.tableWidget_geometry_place.rowCount() 
        # for i in range(geometry_place):
            # self.tableWidget_geometry_place.removeRow(0)
        # # # self.comboBox_posizione.addItems(self.UTILITY.remove_dup_from_list(geometry_list))
        # if self.STATUS_ITEMS[self.BROWSE_STATUS] == "Trova" or "Finden" or "Find":
             # self.tableWidget_geometry_place.removeRow(0)
        # elif self.STATUS_ITEMS[self.BROWSE_STATUS] == "Usa" or "Aktuell " or "Current":		
            # if len(self.DATA_LIST) > 0:
                # try:
        self.delegateMater = ComboBoxDelegate()
        self.delegateMater.def_values(a)
        self.delegateMater.def_editable('True')
        
        # self.delegateMater1 = ComboBoxDelegate()
        # self.delegateMater1.def_values(geometry_list_1)
        # self.delegateMater1.def_editable('True')
        
        self.tableWidget_geometry_place.setItemDelegateForColumn(0,self.delegateMater)
        #if self.comboBox_location.currentIndexChanged:
            
        #self.tableWidget_geometry_place.setItemDelegateForColumn(0,self.delegateMater1)            
                # except Exception as e 
                   # print(str(e))
    
    # def geometry_exp2(self):
        # #self.tableWidget_geometry_place.update()
        # sito = str(self.comboBox_location.currentText())
        # area = str(self.comboBox_name_site.currentText())
        
        # try:  
            # search_dict = {
                # 'location': "'" + sito + "'",
                # 'name_f_l': "'" + area + "'"
            # }
        
        
            # geometry_vl = self.DB_MANAGER.query_bool(search_dict,'SITE_LINE')
            # geometry_list = []
            
            # for i in range(len(geometry_vl)):
                # geometry_list.append(str(geometry_vl[i].coord))
            # # self.tableWidget_geometry_place.clear()
            # # self.tableWidget_geometry_place.update()
            # self.delegateMater = ComboBoxDelegate()
            # self.delegateMater.def_values(geometry_list)
            # self.delegateMater.def_editable('True')
            # self.tableWidget_geometry_place.setItemDelegateForColumn(0,self.delegateMater)    
        # except Exception as e:
            # QMessageBox.information(self, "Record",  str(e))
        
    def enable_button(self, n):
        """This method Unable or Enable the GUI buttons on browse modality"""
        self.pushButton_connect.setEnabled(n)
        self.pushButton_new_rec.setEnabled(n)
        self.pushButton_view_all.setEnabled(n)
        self.pushButton_first_rec.setEnabled(n)
        self.pushButton_last_rec.setEnabled(n)
        self.pushButton_prev_rec.setEnabled(n)
        self.pushButton_next_rec.setEnabled(n)
        self.pushButton_delete.setEnabled(n)
        self.pushButton_new_search.setEnabled(n)
        self.pushButton_search_go.setEnabled(n)
        self.pushButton_sort.setEnabled(n)
    def enable_button_search(self, n):
        """This method Unable or Enable the GUI buttons on searching modality"""
        self.pushButton_connect.setEnabled(n)
        self.pushButton_new_rec.setEnabled(n)
        self.pushButton_view_all.setEnabled(n)
        self.pushButton_first_rec.setEnabled(n)
        self.pushButton_last_rec.setEnabled(n)
        self.pushButton_prev_rec.setEnabled(n)
        self.pushButton_next_rec.setEnabled(n)
        self.pushButton_delete.setEnabled(n)
        self.pushButton_save.setEnabled(n)
        self.pushButton_sort.setEnabled(n)
    def on_pushButton_connect_pressed(self):
        """This method establishes a connection between GUI and database"""
        conn = Connection()
        conn_str = conn.conn_str()
        test_conn = conn_str.find('sqlite')
        if test_conn == 0:
            self.DB_SERVER = "sqlite"
        try:
            self.DB_MANAGER = Hff_db_management(conn_str)
            self.DB_MANAGER.connection()
            self.charge_records()  # charge records from DB
            # check if DB is empty
            if bool(self.DATA_LIST):
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.BROWSE_STATUS = 'b'
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.charge_list()
                self.fill_fields()
            else:
                QMessageBox.warning(self,"WELCOME HFF user", "Welcome in HFF survey:" + " Eamena form\n" + " The DB is empty. Push 'Ok' and Good Work!",
                                    QMessageBox.Ok)
                self.charge_list()
                self.BROWSE_STATUS = 'x'
                self.on_pushButton_new_rec_pressed()
        except Exception as e:
            e = str(e)
            if e.find("no such table"):
                msg = "The connection failed {}. " \
                      "You MUST RESTART QGIS or bug detected! Report it to the developer".format(str(e))
            else:
                msg = "Warning bug detected! Report it to the developer. Error: ".format(str(e))
                self.iface.messageBar().pushMessage(self.tr(msg), Qgis.Warning, 0)
    def customize_GUI(self):
        self.tableWidget_role.setSortingEnabled(False)
        try:
          
            valuesMater = ["Academic Researcher","EAMENA Project Staff","Government Authority/Staff","MarEA Project Staff","Non-Governmental Organisation (NGO)","Private sector","Student/Trainee","Volunteer/Independent Researcher",""]
            self.delegateMater = ComboBoxDelegate()
            self.delegateMater.def_values(valuesMater)
            self.delegateMater.def_editable('True')
            self.tableWidget_role.setItemDelegateForColumn(0,self.delegateMater)
            
            valuesMater2 = ["Aerial Survey","Archaeological Assessment/Ground Survey","Architectural Survey","Condition Assessment","Emergency Impact Assessment","Diver Survey","Marine Geophysical Survey","Risk Assessment","Salvage Recording","Emergency Impact Assessment (Image Interpretation)","Archaeological Assessment (Image Interpretation)","Archaeological Assessment (Marine Geophysical Data Interpretation)","Condition Assessment (Marine Geophysical Data Interpretation)","Condition Assessment (Image Interpretation)","Risk Assessment (Image Interpretation)","Literature Interpretation/Digitisation","Data Cleaning/enhancing",""]
            self.delegateMater2 = ComboBoxDelegate()
            self.delegateMater2.def_values(valuesMater2)
            self.delegateMater2.def_editable('True')
            self.tableWidget_activity.setItemDelegateForColumn(0,self.delegateMater2)
            
            
            valuesMO = [""]
            self.delegateMO = ComboBoxDelegate()
            self.delegateMO.def_values(valuesMO)
            self.delegateMO.def_editable('True')
            self.tableWidget_name.setItemDelegateForColumn(0,self.delegateMO)
            valuesCO = ["Alternative Reference","Toponym","Designation",""]
            self.delegateCO = ComboBoxDelegate()
            self.delegateCO.def_values(valuesCO)
            self.delegateCO.def_editable('True')
            self.tableWidget_nametype.setItemDelegateForColumn(0,self.delegateCO)
            valuesRS = ["Bank/Earthwork","Bank/Wall","Cave","Cleared Area","Colour/Texture Difference","Craft/Vessel/Vehicle","Depression/Hollow","Ditch/Trench","Large Mound","Modified Rock Surface","Multi-Component","Object","Paved/Laid Surface","Pit/Shaft/Tunnel","Plant/Tree","Platform/Terrace","Pyramid/Ziggurat","Rubble Spread/Architectural Fragments","Scatter","Small Mound/Cairn","Structure","Tower","Unknown","Upright Stone","Wall","Waterfront",""]
            self.delegateRS = ComboBoxDelegate()
            self.delegateRS.def_values(valuesRS)
            self.delegateRS.def_editable('True')
            self.tableWidget_fform.setItemDelegateForColumn(0,self.delegateRS)
            valuesDoc = ["Not Applicable","Negligible","Low","Medium","High","Definite",""]
            self.delegateDoc = ComboBoxDelegate()
            self.delegateDoc.def_values(valuesDoc)
            self.delegateDoc.def_editable('True')
            self.tableWidget_fcertainty.setItemDelegateForColumn(0,self.delegateDoc)
            valuesFT = ["Circular"," Curvilinear"," Irregular"," Multiple"," Polygonal"," Rectangular/Square"," Rectilinear"," Semi-circular"," Straight"," Sub-circular"," Sub-rectangular"," Triangular"," Winding","Zigzag","Unknown",""]
            self.delegateFT = ComboBoxDelegate()
            self.delegateFT.def_values(valuesFT)
            self.delegateFT.def_editable('True')
            self.tableWidget_fshape.setItemDelegateForColumn(0,self.delegateFT)
            valuesFT1 = ["Adjoining","Concentric","Clustered","Converging","Dispersed","Discrete","Isolated","Linear","Multiple","Nucleated","Parallel","Perpendicular","Overlapping","Rectilinear","Unknown",""]
            self.delegateFT1 = ComboBoxDelegate()
            self.delegateFT1.def_values(valuesFT1)
            self.delegateFT1.def_editable('True')
            self.tableWidget_farrangement.setItemDelegateForColumn(0,self.delegateFT1)
            valuesFT2 = ["1","2 to 5","6 to 10","11 to 20","21 to 50","51 to 100","100 to 500","500+","Unknown",""]
            self.delegateFT2 = ComboBoxDelegate()
            self.delegateFT2.def_values(valuesFT2)
            self.delegateFT2.def_editable('True')
            self.tableWidget_fnumber.setItemDelegateForColumn(0,self.delegateFT2)
            valuesFT3 = [""]
            self.delegateFT3 = ComboBoxDelegate()
            self.delegateFT3.def_values(valuesFT3)
            self.delegateFT3.def_editable('True')
            self.tableWidget_fassignementinv.setItemDelegateForColumn(0,self.delegateFT3)
            valuesFT5 = ["Aircraft","Altar","Amphitheatre","Anchor","Anchorage","AnimalPen","Aqueduct","Ballast","Barrack","Barrage/Dam","Basilica(Roman","Basin/Tank","Bath-house","Battlefield","Boundary/Barrier","Bridge","Building","Building/Enclosure","Bunker","BurntArea","Camp(temporary","Canal","Caravanserai/Khan","Cemetery","Channel","Church/Chapel","Circus/Hippodrome","Cistern","ClearancePile","ColonnadedStreet","Column/Obelisk","CrossbarArrangement(Gate)","Dolmen","Education/AthleticsBuilding","Emplacement/Foxhole","Enclosure","Farm","FarmBuilding","FieldSystem","FishPond","FishTrap/Weir","Flooring/Mosaic/Paving","Fort/Fortress/Castle","Fountain","FuneraryComplex","Gateway/Arch/Intersection","GatheringArea","Government/AdministrativeBuilding","Grove/Garden/Orchard","Hearth/Oven","Hostelry","House/Dwelling","HuntingHide/Trap","Inscription/RockArt/Relief","Kiln/Forge/Furnace","Kite","LandingPlace","LargeCircle","Latrine/Toilet","Lighthouse","ManagedSite","Market/CommercialUnit","MegalithicFeature","Midden/WasteDeposit","Mill(water)","Mill(wind)","Mill/Quern/GrindstoneElement","Minaret","Mine/Quarry/Extraction","MonasticComplex","Mosque/Imam/Marabout","Mosque/MadrasaComplex","Palace/HighStatusComplex","Pendant","Pier/Jetty/Breakwater/Mole","Pontoon/Mooring","Port/Harbour","Portico/Stoa","Press/PressElement","Production/Processing(Agricultural)","Production/Processing(Animal/'Killsite')","Production/Processing(Glass)","Production/Processing(KnappingFloor/Stonerocessing)","Production/Processing(Metal)","Production/Processing(Pottery)","Production/Processing(Salt)","Production/Processing(Unclassified)","Qanat/Foggara","Quay/Wharf","Railway","RailwayStationStop","Ramparts/Fortification/DefensiveEarthwork","Reservoir/Birka","RingedTomb","Road/Track","Sarcophagus/Coffin","School/University","Sculpture/Statue","Settlement/HabitationSite","Ship/Wreck","Canoe","CargoVessel","Dhow","Galley","Logboat","SailingVessel","Steamship","Submarine","Warship","Shipyard/BoatConstruction","SignificantBuilding","Slipway","StandingStone","StorageFacility","Sub-surfaceMaterial","Synagogue","Tell","Temple/Sanctuary/Shrine","TentBase/Footing","Theatre/Odeon","ThreshingFloor","Tomb/Grave/Burial","WadiWall","Watchtower/ObservationPost","WaterControlMechanism/Feature","Waterwheel","Waymarker","Well","Wheel/Jellyfish","Unknown",""]
            self.delegateFT5 = ComboBoxDelegate()
            self.delegateFT5.def_values(valuesFT5)
            self.delegateFT5.def_editable('True')
            self.tableWidget_interpretationtype.setItemDelegateForColumn(0,self.delegateFT5)
            valuesFT4 = ["Not Applicable","Negligible","Low","Medium","High","Definite",""]
            self.delegateFT4 = ComboBoxDelegate()
            self.delegateFT4.def_values(valuesFT4)
            self.delegateFT4.def_editable('True')
            self.tableWidget_interpretationcertainty.setItemDelegateForColumn(0,self.delegateFT4)
            valuesFT6 = [""]
            self.delegateFT6 = ComboBoxDelegate()
            self.delegateFT6.def_values(valuesFT6)
            self.delegateFT6.def_editable('True')
            self.tableWidget_interpretationumbertype.setItemDelegateForColumn(0,self.delegateFT6)
            valuesFT7 = ["Agricultural/Pastoral","Defensive/Fortification","Domestic","Educational","Entertainment/Leisure","Funerary/Memorial","Hunting/Fishing","Hydrological","Industrial/Productive","Infrastructure/Transport","Maritime","Military","Public /Institutional","Religious","Status/Display/Monumental","Trade/Commercial","Unknown",""]
            self.delegateFT7 = ComboBoxDelegate()
            self.delegateFT7.def_values(valuesFT7)
            self.delegateFT7.def_editable('True')
            self.tableWidget_functioninterpretation.setItemDelegateForColumn(0,self.delegateFT7)
        except:         
            pass
    def charge_list(self):
        sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'name_site', 'SITE'))
        try:
            sito_vl.remove('')
        except :
            pass
        self.comboBox_name_site.clear()
        sito_vl.sort()
        self.comboBox_name_site.addItems(sito_vl)
        location_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'location_', 'SITE'))
        try:
            location_vl.remove('')
        except :
            pass
        self.comboBox_location.clear()
        location_vl.sort()
        self.comboBox_location.addItems(location_vl)
        # #lista years reference
        grid = ['E35N33-11','E35N33-12','E35N33-13','E35N33-14','E35N33-21','E35N33-23','E35N33-24','E35N33-31','E35N33-32','E35N33-33','E35N33-34','E35N33-41','E35N33-42','E35N33-43','E35N33-44','E35N34-11','E35N34-12','E35N34-13','E35N34-14','E35N34-21','E35N34-22','E35N34-23','E35N34-24','E35N34-31','E35N34-32','E35N34-41','E35N34-42','E36N33-31','E36N33-33','E36N33-34','E36N34-11','E36N34-12','E36N34-13','E36N34-14','E36N34-21','E36N34-23','E36N34-31','E36N34-32']
        self.comboBox_grid.clear()
        self.comboBox_grid.addItems(grid)
    def on_pushButton_sort_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            dlg = SortPanelMain(self)
            dlg.insertItems(self.SORT_ITEMS)
            dlg.exec_()
            items, order_type = dlg.ITEMS, dlg.TYPE_ORDER
            self.SORT_ITEMS_CONVERTED = []
            for i in items:
                self.SORT_ITEMS_CONVERTED.append(self.CONVERSION_DICT[str(i)])
            self.SORT_MODE = order_type
            self.empty_fields()
            id_list = []
            for i in self.DATA_LIST:
                id_list.append(eval("i." + self.ID_TABLE))
            self.DATA_LIST = []
            temp_data_list = self.DB_MANAGER.query_sort(id_list, self.SORT_ITEMS_CONVERTED, self.SORT_MODE,
                                                        self.MAPPER_TABLE_CLASS, self.ID_TABLE)
            for i in temp_data_list:
                self.DATA_LIST.append(i)
            self.BROWSE_STATUS = "b"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            if type(self.REC_CORR) == "<type 'str'>":
                corr = 0
            else:
                corr = self.REC_CORR
            self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
            self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
            self.SORT_STATUS = "o"
            self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
            self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
            self.fill_fields()
    def on_pushButton_new_rec_pressed(self):
        if bool(self.DATA_LIST):
            if self.data_error_check() == 1:
                pass
            else:
                if self.BROWSE_STATUS == "b":
                    if self.DATA_LIST:
                        if self.records_equal_check() == 1:
                            self.update_if(QMessageBox.warning(self, 'Error',
                                                               "The record has been changed. Do you want to save the changes?",
                                                               QMessageBox.Ok | QMessageBox.Cancel))
                            # set the GUI for a new record
        if self.BROWSE_STATUS != "n":
            self.BROWSE_STATUS = "n"
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.empty_fields()
            self.setComboBoxEnable(["self.comboBox_name_site"], "True")
            self.setComboBoxEditable(["self.comboBox_name_site"], 1)
            self.setComboBoxEnable(["self.comboBox_location"], "True")
            self.setComboBoxEditable(["self.comboBox_location"], 1)
            self.SORT_STATUS = "n"
            self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
            self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
            self.set_rec_counter('', '')
            self.label_sort.setText(self.SORTED_ITEMS["n"])
            self.empty_fields()
            self.enable_button(0)
    def on_pushButton_save_pressed(self):
        # save record
        if self.BROWSE_STATUS == "b":
            if self.data_error_check() == 0:
                if self.records_equal_check() == 1:
                    self.update_if(QMessageBox.warning(self, 'Error',
                                                       "The record has been changed. Do you want to save the changes?",
                                                       QMessageBox.Ok | QMessageBox.Cancel))
                    self.empty_fields()
                    self.SORT_STATUS = "n"
                    self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
                    self.enable_button(1)
                    self.fill_fields(self.REC_CORR)
                else:
                    QMessageBox.warning(self, "Warning", "No changes have been made", QMessageBox.Ok)
        else:
            if self.data_error_check() == 0:
                test_insert = self.insert_new_rec()
                if test_insert == 1:
                    self.empty_fields()
                    self.label_sort.setText(self.SORTED_ITEMS["n"])
                    self.charge_list()
                    self.charge_records()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                    self.setComboBoxEnable(["self.comboBox_name_site"], "False")
                    self.setComboBoxEnable(["self.comboBox_location"], "False")
                    self.fill_fields(self.REC_CORR)
                    self.enable_button(1)
                else:
                    pass
    def data_error_check(self):
        test = 0
        EC = Error_check()
        if EC.data_is_empty(str(self.comboBox_name_site.currentText())) == 0:
            QMessageBox.warning(self, "WARNING", "Name site \n The field must not be empty", QMessageBox.Ok)
            test = 1
        return test
    def insert_new_rec(self):
        role= self.table2dict("self.tableWidget_role")
        activity= self.table2dict("self.tableWidget_activity")
        investigator= self.table2dict("self.tableWidget_investigator")
        date_activity= self.table2dict("self.tableWidget_date_activity") 
        hplacetype= self.table2dict("self.tableWidget_hplacetype") 
        hplacefuntion= self.table2dict("self.tableWidget_hplacefuntion") 
        hplacefunctioncertainty= self.table2dict("self.tableWidget_hplacefunctioncertainty") 
        geometry_place= self.table2dict("self.tableWidget_geometry_place") 
        site_location_certainty= self.table2dict("self.tableWidget_site_location_certainty") 
        geometry_extent= self.table2dict("self.tableWidget_geometry_extent") 
        country_type= self.table2dict("self.tableWidget_country_type") 
        overall_condition_state = self.table2dict("self.tableWidget_overall_condition_state") 
        damage= self.table2dict("self.tableWidget_damage") 
        disturbance_cause= self.table2dict("self.tableWidget_disturbance_cause") 
        disturbance_cause_2= self.table2dict("self.tableWidget_disturbance_cause_2") 
        effect_type= self.table2dict("self.tableWidget_effect_type") 
        effect_certainty= self.table2dict("self.tableWidget_effect_certainty") 
        threat_type= self.table2dict("self.tableWidget_threat_type") 
        threat_probability= self.table2dict("self.tableWidget_threat_probability") 
        topography_type= self.table2dict("self.tableWidget_topography_type") 
        oac=  self.table2dict("self.tableWidget_overall_arch_cert")
        osm=  self.table2dict("self.tableWidget_overall_site_morph")
        cpc=  self.table2dict("self.tableWidget_cultural_period_cert")
        cspc= self.table2dict("self.tableWidget_cultural_sub_period_cert")
        spc=   self.table2dict("self.tableWidget_sub_period_cert")
        sfft=  self.table2dict("self.tableWidget_site_features_from_type")
        sfftc= self.table2dict("self.tableWidget_site_feature_from_type_cert")
        sfst=  self.table2dict("self.tableWidget_site_feature_shape_type")
        sfat=  self.table2dict("self.tableWidget_site_feature_arrangement_type")
        sfnt=  self.table2dict("self.tableWidget_site_feature_number_type")
        sfit=  self.table2dict("self.tableWidget_site_feature_interpretation_type")
        sfin=  self.table2dict("self.tableWidget_site_feature_interpretation_number")
        sic=   self.table2dict("self.tableWidget_site_interpretation_cert")
        built= self.table2dict("self.tableWidget_built")
        hpr=    self.table2dict("self.tableWidget_hp_related")
        mu=  self.table2dict("self.tableWidget_measurement_unit")
        dt=  self.table2dict("self.tableWidget_dimension_type")
        mst= self.table2dict("self.tableWidget_measurement_siurce_type")
        
        
        
        
        try:
            data = self.DB_MANAGER.insert_eamena_values(
                self.DB_MANAGER.max_num_id(self.MAPPER_TABLE_CLASS, self.ID_TABLE) + 1,
                str(self.comboBox_location.currentText()),  # 1 - Sito
                str(investigator),
                str(role),
                str(activity),
                str(date_activity),
                str(self.comboBox_ge_assessment.currentText()),  # 3 - regione
                self.mDateEdit_1.text(), # 8 - path
                str(self.comboBox_information_resource_used.currentText()),  # 3 - regione
                str(self.mDateEdit_2.text()), # 8 - path
                str(self.comboBox_name_site.currentText()),  
                str(self.comboBox_resource_type.currentText()),  
                str(hplacetype),
                str(self.comboBox_general_description_type.currentText()), 
                str(self.textEdit_general_description.toPlainText()),  
                str(hplacefuntion),
                str(hplacefunctioncertainty),
                str(self.comboBox_designation.currentText()),
                str(self.mDateEdit_3.text()), 
                str(self.mDateEdit_4.text()),
                str(geometry_place),
                str(self.comboBox_geometry_qualifier.currentText()),  
                str(site_location_certainty),
                str(geometry_extent),
                str(self.comboBox_site_overall_shape_type.currentText()),
                str(self.comboBox_grid.currentText()),  
                str(country_type),
                str(self.comboBox_cadastral_reference.currentText()),  # 4 - comune
                str(self.comboBox_resource_orientation.currentText()),  # 4 - comune
                str(self.comboBox_Address.currentText()),  # 4 - comune
                str(self.comboBox_address_type.currentText()),  # 4 - comune
                str(self.comboBox_administrative_subvision.currentText()),  # 4 - comune
                str(self.comboBox_administrative_subvision_type.currentText()), 
                str(oac),
                str(osm),
                str(self.comboBox_cultural_period.currentText()),
                str(cpc),
                str(cspc),
                str(spc),
                str(self.comboBox_date_inference.currentText()),
                str(self.comboBox_arch_date.currentText()),
                str(self.comboBox_arch_date_to.currentText()),
                str(self.mDateEdit_9.text()),
                str(self.mDateEdit_10.text()),
                str(self.mDateEdit_11.text()),
                str(self.mDateEdit_12.text()),
                str(self.mDateEdit_13.text()),
                str(self.mDateEdit_14.text()),
                str(sfft),
                str(sfftc),
                str(sfst),
                str(sfat),
                str(sfnt),
                str(sfit),
                str(sfin),
                str(sic),
                str(built),
                str(hpr),
                str(self.comboBox_material_class.currentText()),
                str(self.comboBox_material_type.currentText()),
                str(self.comboBox_contruction_tech.currentText()),
                str(self.comboBox_measurement_number.currentText()),
                str(mu), 
                str(dt), 
                str(mst),        
                str(self.comboBox_related_geoarch.currentText()),
                str(overall_condition_state),
                str(damage),
                str(self.comboBox_disturbance_cause_category.currentText()),  # 4 - comune
                str(disturbance_cause),
                str(disturbance_cause_2),
                str(self.mDateEdit_5.text()),
                str(self.mDateEdit_6.text()),
                str(self.mDateEdit_7.text()),
                str(self.mDateEdit_8.text()),
                str(self.comboBox_disturbance_cause_ass.currentText()),
                str(effect_type),
                str(effect_certainty),
                str(self.comboBox_threat_category.currentText()),  # 4 - comune
                str(threat_type),
                str(threat_probability),
                str(self.comboBox_threat.currentText()),  # 4 - comune
                str(self.comboBox_int_activity_type.currentText()),  # 4 - comune
                str(self.comboBox_raccomandation.currentText()),  # 4 - comune
                str(self.comboBox_priority.currentText()),  # 4 - comune
                str(self.comboBox_related.currentText()),  # 4 - comune
                str(topography_type),
                str(self.comboBox_land_cover_type.currentText()),  # 4 - comune
                str(self.comboBox_land_cover_assessment.currentText()),  # 4 - comune
                str(self.comboBox_surficial.currentText()),  # 4 - comune
                str(self.comboBox_depositional.currentText()),  # 4 - comune
                str(self.comboBox_bedrock.currentText()),  # 4 - comune
                str(self.comboBox_fetch.currentText()),  # 4 - comune
                str(self.comboBox_wave.currentText()),  # 4 - comune
                str(self.comboBox_tidal_energy.currentText()),  # 4 - comune
                str(self.comboBox_depth_max.currentText()),  # 4 - comune
                str(self.comboBox_depth_min.currentText()),  # 4 - comune
                str(self.comboBox_datum_type.currentText()),  # 4 - comune
                str(self.comboBox_datum_description.currentText()),  # 4 - comune
                str(self.comboBox_restricted.currentText()),  # 4 - comune
               
                )
            try:
                self.DB_MANAGER.insert_data_session(data)
                return 1
            except Exception as e:
                e_str = str(e)
                if e_str.__contains__("IntegrityError"):
                    msg = self.ID_TABLE + " exist in db"
                    QMessageBox.warning(self, "Error", "Error" + str(msg), QMessageBox.Ok)
                else:
                    msg = e
                    QMessageBox.warning(self, "Error", "Error 1 \n" + str(msg), QMessageBox.Ok)
                return 0
        except AssertionError as e:
            QMessageBox.warning(self, "Error", "Error 2 \n" + str(e), QMessageBox.Ok)
            return 0
    #'''button to manage tablewidgets'''
    def on_pushButton_add_assessment_pressed(self):
        self.insert_new_row('self.tableWidget_investigator')
        self.insert_new_row('self.tableWidget_role')
        self.insert_new_row('self.tableWidget_activity')
        self.insert_new_row('self.tableWidget_date_activity')
    def on_pushButton_remove_assessment_pressed(self):
        self.remove_row('self.tableWidget_investigator')
        self.remove_row('self.tableWidget_role')
        self.remove_row('self.tableWidget_activity')
        self.remove_row('self.tableWidget_date_activity')
    def on_pushButton_add_resource_pressed(self):
        self.insert_new_row('self.tableWidget_hplacetype')
        self.insert_new_row('self.tableWidget_hplacefuntion')
        self.insert_new_row('self.tableWidget_hplacefunctioncertainty')
    def on_pushButton_remove_resource_pressed(self):
        self.remove_row('self.tableWidget_hplacetype')
        self.remove_row('self.tableWidget_hplacefuntion')
        self.remove_row('self.tableWidget_hplacefunctioncertainty')
    def on_pushButton_add_geometry_pressed(self):
        self.insert_new_row('self.tableWidget_geometry_place')
        self.insert_new_row('self.tableWidget_site_location_certainty')
        self.insert_new_row('self.tableWidget_geometry_extent')
        self.insert_new_row('self.tableWidget_country_type')
    def on_pushButton_remove_geometry_pressed(self):
        self.remove_row('self.tableWidget_geometry_place')
        self.remove_row('self.tableWidget_site_location_certainty')
        self.remove_row('self.tableWidget_geometry_extent')
        self.remove_row('self.tableWidget_country_type')
    def on_pushButton_add_condition_pressed(self):
        self.insert_new_row('self.tableWidget_overall_condition_state')
        self.insert_new_row('self.tableWidget_damage')
        self.insert_new_row('self.tableWidget_disturbance_cause')
        self.insert_new_row('self.tableWidget_disturbance_cause_2')
        self.insert_new_row('self.tableWidget_effect_type')
        self.insert_new_row('self.tableWidget_effect_certainty')
        self.insert_new_row('self.tableWidget_threat_type')
        self.insert_new_row('self.tableWidget_threat_probability')
    def on_pushButton_remove_condition_pressed(self):
        self.remove_row('self.tableWidget_overall_condition_state')
        self.remove_row('self.tableWidget_damage')
        self.remove_row('self.tableWidget_disturbance_cause')
        self.remove_row('self.tableWidget_disturbance_cause_2')
        self.remove_row('self.tableWidget_effect_type')
        self.remove_row('self.tableWidget_effect_certainty')
        self.remove_row('self.tableWidget_threat_type')
        self.remove_row('self.tableWidget_threat_probability')
    def on_pushButton_add_topography_pressed(self):
        self.insert_new_row('self.tableWidget_topography_type')
    def on_pushButton_remove_topography_pressed(self):
        self.remove_row('self.tableWidget_topography_type')
    def on_pushButton_add_arch_pressed(self):
        self.insert_new_row('self.tableWidget_overall_arch_cert')
        self.insert_new_row('self.tableWidget_overall_site_morph')
        self.insert_new_row('self.tableWidget_cultural_period_cert')
        self.insert_new_row('self.tableWidget_cultural_sub_period_cert')
        self.insert_new_row('self.tableWidget_sub_period_cert')
        self.insert_new_row('self.tableWidget_site_features_from_type')
        self.insert_new_row('self.tableWidget_site_feature_from_type_cert')
        self.insert_new_row('self.tableWidget_site_feature_shape_type')
        self.insert_new_row('self.tableWidget_site_feature_arrangement_type')
        self.insert_new_row('self.tableWidget_site_feature_number_type')
        self.insert_new_row('self.tableWidget_site_feature_interpretation_type')
        self.insert_new_row('self.tableWidget_site_feature_interpretation_number')
        
        self.insert_new_row('self.tableWidget_site_interpretation_cert')
        self.insert_new_row('self.tableWidget_built')
        self.insert_new_row('self.tableWidget_hp_related')
        self.insert_new_row('self.tableWidget_measurement_unit')
        self.insert_new_row('self.tableWidget_dimension_type')
        self.insert_new_row('self.tableWidget_measurement_siurce_type')
    def on_pushButton_remove_arch_pressed(self):
        self.remove_row('self.tableWidget_overall_arch_cert')
        self.remove_row('self.tableWidget_overall_site_morph')
        self.remove_row('self.tableWidget_cultural_period_cert')
        self.remove_row('self.tableWidget_cultural_sub_period_cert')
        self.remove_row('self.tableWidget_sub_period_cert')
        self.remove_row('self.tableWidget_site_features_from_type')
        self.remove_row('self.tableWidget_site_feature_from_type_cert')
        self.remove_row('self.tableWidget_site_feature_shape_type')
        self.remove_row('self.tableWidget_site_feature_arrangement_type')
        self.remove_row('self.tableWidget_site_feature_number_type')
        self.remove_row('self.tableWidget_site_feature_interpretation_type')
        self.remove_row('self.tableWidget_site_feature_interpretation_number')
        
        self.remove_row('self.tableWidget_site_interpretation_cert')
        self.remove_row('self.tableWidget_built')
        self.remove_row('self.tableWidget_hp_related')
        self.remove_row('self.tableWidget_measurement_unit')
        self.remove_row('self.tableWidget_dimension_type')
        self.remove_row('self.tableWidget_measurement_siurce_type')
    
    
    def insert_new_row(self, table_name):
        """insert new row into a table based on table_name"""
        cmd = table_name + ".insertRow(0)"
        eval(cmd)
    def tableInsertData(self, t, d):
        """Set the value into alls Grid"""
        self.table_name = t
        self.data_list = eval(d)
        #self.data_list.sort()
        # column table count
        table_col_count_cmd = "{}.columnCount()".format(self.table_name)
        table_col_count = eval(table_col_count_cmd)
        # clear table
        table_clear_cmd = "{}.clearContents()".format(self.table_name)
        eval(table_clear_cmd)
        for i in range(table_col_count):
            table_rem_row_cmd = "{}.removeRow(int({}))".format(self.table_name, i)
            eval(table_rem_row_cmd)
            
        for row in range(len(self.data_list)):
            cmd = '{}.insertRow(int({}))'.format(self.table_name, row)
            eval(cmd)
            for col in range(len(self.data_list[row])):
                
                exec_str = '{}.setItem(int({}),int({}),QTableWidgetItem(self.data_list[row][col]))'.format(
                    self.table_name, row, col)
                eval(exec_str)
    def remove_row(self, table_name):
        """insert new row into a table based on table_name"""
        
        cmd = ("%s.removeRow(0)") % (table_name)
        eval(cmd)
    def check_record_state(self):
        ec = self.data_error_check()
        if ec == 1:
            return 1  
        elif self.records_equal_check() == 1 and ec == 0:
            
            return 0  
    def on_pushButton_view_all_pressed(self):
        self.empty_fields()
        self.charge_records()
        self.fill_fields()
        self.BROWSE_STATUS = "b"
        self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
        if type(self.REC_CORR) == "<class 'str'>":
            corr = 0
        else:
            corr = self.REC_CORR
        self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
        self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
        self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
        self.SORT_STATUS = "n"
        self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
        
    def on_pushButton_first_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            try:
                self.empty_fields()
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.fill_fields(0)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except :
                    pass
    def on_pushButton_last_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            try:
                self.empty_fields()
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), len(self.DATA_LIST) - 1
                self.fill_fields(self.REC_CORR)
                self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
            except :
                    pass
    def on_pushButton_prev_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.REC_CORR = self.REC_CORR - 1
            if self.REC_CORR == -1:
                self.REC_CORR = 0
                QMessageBox.warning(self, "Warning", "You are to the first record!", QMessageBox.Ok)
            else:
                try:
                    self.empty_fields()
                    self.fill_fields(self.REC_CORR)
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                except :
                    pass
    def on_pushButton_next_rec_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.REC_CORR = self.REC_CORR + 1
            if self.REC_CORR >= self.REC_TOT:
                self.REC_CORR = self.REC_CORR - 1
                QMessageBox.warning(self, "Error", "You are to the first record!", QMessageBox.Ok)
            else:
                try:
                    self.empty_fields()
                    self.fill_fields(self.REC_CORR)
                    self.set_rec_counter(self.REC_TOT, self.REC_CORR + 1)
                except :
                    pass
    def on_pushButton_delete_pressed(self):
        msg = QMessageBox.warning(self, "Warning!!!",
                                  "Do you really want to break the record? \n Action is irreversible.",
                                  QMessageBox.Ok | QMessageBox.Cancel)
        if msg == QMessageBox.Cancel:
            QMessageBox.warning(self, "Message!!!", "Action deleted!")
        else:
            try:
                id_to_delete = eval("self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE)
                self.DB_MANAGER.delete_one_record(self.TABLE_NAME, self.ID_TABLE, id_to_delete)
                self.charge_records()  
                QMessageBox.warning(self, "Message!!!", "Record deleted!")
            except Exception as e:
                QMessageBox.warning(self, "Message!!!", "error type: " + str(e))
            if not bool(self.DATA_LIST):
                QMessageBox.warning(self, "Warning", "the db is empty!", QMessageBox.Ok)
                self.DATA_LIST = []
                self.DATA_LIST_REC_CORR = []
                self.DATA_LIST_REC_TEMP = []
                self.REC_CORR = 0
                self.REC_TOT = 0
                self.empty_fields()
                self.set_rec_counter(0, 0)
                
            if bool(self.DATA_LIST):
                self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                self.charge_list()
                self.fill_fields()
        self.SORT_STATUS = "n"
        self.label_sort.setText(self.SORTED_ITEMS[self.SORT_STATUS])
    def on_pushButton_new_search_pressed(self):
        if self.check_record_state() == 1:
            pass
        else:
            self.enable_button_search(0)
            # set the GUI for a new search
            if self.BROWSE_STATUS != "f":
                self.BROWSE_STATUS = "f"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                
                self.setComboBoxEnable(["self.comboBox_name_site"], "True")
                
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                self.set_rec_counter('', '')
                self.label_sort.setText(self.SORTED_ITEMS["n"])
                self.charge_list()
                self.empty_fields()
    def on_pushButton_search_go_pressed(self):
        if self.BROWSE_STATUS != "f":
            QMessageBox.warning(self, "WARNING", "To perform a new search click on the 'new search' button ",
                                QMessageBox.Ok)
        else:
            search_dict = {
                self.TABLE_FIELDS[0]:"'" +  str(self.comboBox_location.currentText()) +"'",  # 1 - Sito
                self.TABLE_FIELDS[9]:"'" +  str(self.comboBox_name_site.currentText()) +"'",  # 2 - nazione
                self.TABLE_FIELDS[5]:"'" +  str(self.comboBox_ge_assessment.currentText()) +"'",  # 3 - regione
                self.TABLE_FIELDS[6]:"'" +  str(self.mDateEdit_1.text()) +"'", # 8 - path
                self.TABLE_FIELDS[7]:"'" +  str(self.comboBox_information_resource_used.currentText()) +"'",  # 3 - regione
                self.TABLE_FIELDS[8]:"'" +  str(self.mDateEdit_2.text()) +"'", # 8 - path
                self.TABLE_FIELDS[10]:"'" + str(self.comboBox_resource_type.currentText()) +"'",  # 3 - regione
                self.TABLE_FIELDS[12]:"'" + str(self.comboBox_general_description_type.currentText()) +"'",  # 3 - regione
                self.TABLE_FIELDS[16]:"'" + str(self.comboBox_designation.currentText()) +"'",  # 3 - regione
                self.TABLE_FIELDS[17]:"'" + str(self.mDateEdit_3.text()) +"'",  # 3 - regione
                self.TABLE_FIELDS[18]:"'" + str(self.mDateEdit_4.text()) +"'",  # 3 - regione
                self.TABLE_FIELDS[13]:"'" + str(self.textEdit_general_description.toPlainText()) +"'",  # 3 - regione
                
                self.TABLE_FIELDS[20]:"'" + str(self.comboBox_geometry_qualifier.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[23]:"'" + str(self.comboBox_site_overall_shape_type.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[24]:"'" + str(self.comboBox_site_overall_shape_type.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[26]:"'" + str(self.comboBox_cadastral_reference.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[27]:"'" + str(self.comboBox_resource_orientation.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[28]:"'" + str(self.comboBox_Address.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[29]:"'" + str(self.comboBox_address_type.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[30]:"'" + str(self.comboBox_administrative_subvision.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[31]:"'" + str(self.comboBox_administrative_subvision_type.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[70]:"'" + str(self.mDateEdit_5.text()) +"'",  # 4 - comune
                self.TABLE_FIELDS[71]:"'" +  str(self.mDateEdit_6.text()) +"'",  # 4 - comune
                self.TABLE_FIELDS[72]:"'" +  str(self.mDateEdit_7.text()) +"'",  # 4 - comune
                self.TABLE_FIELDS[73]:"'" +  str(self.mDateEdit_8.text()) +"'",  # 4 - comune
                self.TABLE_FIELDS[81]:"'" +  str(self.comboBox_int_activity_type.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[84]:"'" +  str(self.comboBox_related.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[74]:"'" +  str(self.comboBox_disturbance_cause_ass.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[82]:"'" + str(self.comboBox_raccomandation.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[67]:"'" + str(self.comboBox_disturbance_cause_category.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[80]:"'" + str(self.comboBox_threat.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[83]:"'" + str(self.comboBox_priority.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[77]:"'" + str(self.comboBox_threat_category.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[86]:"'" + str(self.comboBox_land_cover_type.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[89]:"'" + str(self.comboBox_depositional.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[92]:"'" + str(self.comboBox_wave.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[96]:"'" + str(self.comboBox_datum_type.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[87]:"'" + str(self.comboBox_land_cover_assessment.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[90]:"'" + str(self.comboBox_bedrock.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[94]:"'" + str(self.comboBox_depth_max.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[97]:"'" + str(self.comboBox_datum_description.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[88]:"'" + str(self.comboBox_surficial.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[91]:"'" + str(self.comboBox_fetch.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[95]:"'" + str(self.comboBox_depth_min.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[93]:"'" + str(self.comboBox_tidal_energy.currentText()) +"'",  # 4 - comune
                self.TABLE_FIELDS[98]:"'" + str(self.comboBox_restricted.currentText()) +"'",  # 4 - comune
                
            }
            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            if not bool(search_dict):
                QMessageBox.warning(self, " WARNING", "No search has been set!!!", QMessageBox.Ok)
            else:
                res = self.DB_MANAGER.query_bool(search_dict, self.MAPPER_TABLE_CLASS)
                if not bool(res):
                    QMessageBox.warning(self, "WARNING", "No record found!", QMessageBox.Ok)
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]
                    self.fill_fields(self.REC_CORR)
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.setComboBoxEnable(["self.comboBox_name_site"], "False")
                else:
                    self.DATA_LIST = []
                    for i in res:
                        self.DATA_LIST.append(i)
                    ##                  if self.DB_SERVER == 'sqlite':
                    ##                      for i in self.DATA_LIST:
                    ##                          self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS, self.ID_TABLE, [i.id_sito], ['find_check'], [1])
                    self.REC_TOT, self.REC_CORR = len(self.DATA_LIST), 0
                    self.DATA_LIST_REC_TEMP = self.DATA_LIST_REC_CORR = self.DATA_LIST[0]  ####darivedere
                    self.fill_fields()
                    self.BROWSE_STATUS = "b"
                    self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                    self.set_rec_counter(len(self.DATA_LIST), self.REC_CORR + 1)
                    if self.REC_TOT == 1:
                        strings = ("It has been found", self.REC_TOT, "record")
                        if self.toolButton_draw_siti.isChecked():
                            sing_layer = [self.DATA_LIST[self.REC_CORR]]
                            self.pyQGIS.charge_eamena_pol_layers(sing_layer)
                            self.pyQGIS.charge_eamena_line_layers(sing_layer)
                            self.pyQGIS.charge_eamena_point_layers(sing_layer)
                    else:
                        strings = ("They have been found", self.REC_TOT, "records")
                        if self.toolButton_draw_siti.isChecked():
                            self.pyQGIS.charge_eamena_pol_layers(self.DATA_LIST)
                            self.pyQGIS.charge_eamena_line_layers(self.DATA_LIST)
                            self.pyQGIS.charge_eamena_point_layers(self.DATA_LIST)
                    self.setComboBoxEnable(["self.comboBox_name_site"], "False")
                    QMessageBox.warning(self, "Message", "%s %d %s" % strings, QMessageBox.Ok)
        self.enable_button_search(1)
    # def on_pushButton_draw_pressed(self):
        # self.pyQGIS.charge_layers_for_draw(["1", "3", "5", "7", "8", "9", "10","11"])
    def on_pushButton_eamena_geometry_pressed(self):
        sito = str(self.comboBox_location.currentText())
        self.pyQGIS.charge_eamena_geometry([],
                                          "location", sito)
    def on_toolButton_draw_siti_toggled(self):
        if self.toolButton_draw_siti.isChecked():
            QMessageBox.warning(self, "Message",
                                "GIS mode active. Now your request will be displayed on the GIS",
                                QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "Message",
                                "GIS mode disabled. Now your request will no longer be displayed on the GIS.",
                                QMessageBox.Ok)
    def update_if(self, msg):
        rec_corr = self.REC_CORR
        if msg == QMessageBox.Ok:
            test = self.update_record()
            if test == 1:
                id_list = []
                for i in self.DATA_LIST:
                    id_list.append(eval("i." + self.ID_TABLE))
                self.DATA_LIST = []
                if self.SORT_STATUS == "n":
                    temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc',
                                                                self.MAPPER_TABLE_CLASS,
                                                                self.ID_TABLE)  # self.DB_MANAGER.query_bool(self.SEARCH_DICT_TEMP, self.MAPPER_TABLE_CLASS) #
                else:
                    temp_data_list = self.DB_MANAGER.query_sort(id_list, self.SORT_ITEMS_CONVERTED, self.SORT_MODE,
                                                                self.MAPPER_TABLE_CLASS, self.ID_TABLE)
                for i in temp_data_list:
                    self.DATA_LIST.append(i)
                self.BROWSE_STATUS = "b"
                self.label_status.setText(self.STATUS_ITEMS[self.BROWSE_STATUS])
                if type(self.REC_CORR) == "<type 'str'>":
                    corr = 0
                else:
                    corr = self.REC_CORR
                return 1
            elif test == 0:
                return 0
                # custom functions
    def charge_records(self):
        self.DATA_LIST = []
        if self.DB_SERVER == 'sqlite':
            for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS):
                self.DATA_LIST.append(i)
        else:
            id_list = []
            for i in self.DB_MANAGER.query(self.MAPPER_TABLE_CLASS):
                id_list.append(eval("i." + self.ID_TABLE))
            temp_data_list = self.DB_MANAGER.query_sort(id_list, [self.ID_TABLE], 'asc', self.MAPPER_TABLE_CLASS,
                                                        self.ID_TABLE)
            for i in temp_data_list:
                self.DATA_LIST.append(i)
    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today
    def table2dict(self, n):
        self.tablename = n
        row = eval(self.tablename + ".rowCount()")
        col = eval(self.tablename + ".columnCount()")
        lista = []
        for r in range(row):
            sub_list = []
            for c in range(col):
                value = eval(self.tablename + ".item(r,c)")
                if bool(value):
                    sub_list.append(str(value.text()))
            lista.append(sub_list)
        return lista
    def empty_fields(self):
        
        role= self.tableWidget_role.rowCount()
        activity= self.tableWidget_activity.rowCount()
        investigator= self.tableWidget_investigator.rowCount()
        date_activity= self.tableWidget_date_activity.rowCount() 
        hplacetype= self.tableWidget_hplacetype.rowCount() 
        hplacefuntion= self.tableWidget_hplacefuntion.rowCount() 
        hplacefunctioncertainty= self.tableWidget_hplacefunctioncertainty.rowCount() 
        geometry_place= self.tableWidget_geometry_place.rowCount() 
        site_location_certainty= self.tableWidget_site_location_certainty.rowCount() 
        geometry_extent= self.tableWidget_geometry_extent.rowCount() 
        country_type= self.tableWidget_country_type.rowCount() 
        overall_condition_state = self.tableWidget_overall_condition_state.rowCount() 
        damage= self.tableWidget_damage.rowCount() 
        disturbance_cause= self.tableWidget_disturbance_cause.rowCount() 
        disturbance_cause_2= self.tableWidget_disturbance_cause_2.rowCount() 
        effect_type= self.tableWidget_effect_type.rowCount() 
        effect_certainty= self.tableWidget_effect_certainty.rowCount() 
        threat_type= self.tableWidget_threat_type.rowCount() 
        threat_probability= self.tableWidget_threat_probability.rowCount() 
        topography_type= self.tableWidget_topography_type.rowCount() 
        oac=  self.tableWidget_overall_arch_cert.rowCount()
        osm=  self.tableWidget_overall_site_morph.rowCount()
        cpc=  self.tableWidget_cultural_period_cert.rowCount()
        cspc= self.tableWidget_cultural_sub_period_cert.rowCount()
        spc=   self.tableWidget_sub_period_cert.rowCount()
        sfft=  self.tableWidget_site_features_from_type.rowCount()
        sfftc= self.tableWidget_site_feature_from_type_cert.rowCount()
        sfst=  self.tableWidget_site_feature_shape_type.rowCount()
        sfat=  self.tableWidget_site_feature_arrangement_type.rowCount()
        sfnt=  self.tableWidget_site_feature_number_type.rowCount()
        sfit=  self.tableWidget_site_feature_interpretation_type.rowCount()
        sfin=  self.tableWidget_site_feature_interpretation_number.rowCount()
        sic=   self.tableWidget_site_interpretation_cert.rowCount()
        built= self.tableWidget_built.rowCount()
        hpr=    self.tableWidget_hp_related.rowCount()
        mu=  self.tableWidget_measurement_unit.rowCount()
        dt=  self.tableWidget_dimension_type.rowCount()
        mst= self.tableWidget_measurement_siurce_type.rowCount()
        
        self.comboBox_location.setEditText('')  # 1 - Sito
        for i in range(investigator):
            self.tableWidget_investigator.removeRow(0)
        #self.insert_new_row("self.tableWidget_investigator")
        for i in range(role):
            self.tableWidget_role.removeRow(0)
        #self.insert_new_row("self.tableWidget_role")
        for i in range(activity):
            self.tableWidget_activity.removeRow(0)        
        #self.insert_new_row("self.tableWidget_activity")
        for i in range(date_activity):
            self.tableWidget_date_activity.removeRow(0)
        #self.insert_new_row("self.tableWidget_date_activity")
        self.comboBox_ge_assessment.setEditText('')  # 3 - regione
        self.mDateEdit_1.text() # 8 - path
        self.comboBox_information_resource_used.setEditText('')  # 3 - regione
        self.mDateEdit_2.clear() # 8 - path
        self.comboBox_name_site.setEditText('')  
        self.comboBox_resource_type.setEditText('')  
        
        
        for i in range(hplacetype):
            self.tableWidget_hplacetype.removeRow(0)
        #self.insert_new_row("self.tableWidget_hplacetype")
        self.comboBox_general_description_type.setEditText('') 
        self.textEdit_general_description.clear()  
        for i in range(hplacefuntion):
            self.tableWidget_hplacefuntion.removeRow(0)
        #self.insert_new_row("self.tableWidget_hplacefuntion")
        for i in range(hplacefunctioncertainty):
            self.tableWidget_hplacefunctioncertainty.removeRow(0)
        #self.insert_new_row("self.tableWidget_hplacefunctioncertainty")
        self.comboBox_designation.setEditText('')
        self.mDateEdit_3.clear() 
        self.mDateEdit_4.clear()
        for i in range(geometry_place):
            self.tableWidget_geometry_place.removeRow(0)
        #self.insert_new_row("self.tableWidget_geometry_place")
        self.comboBox_geometry_qualifier.setEditText('')  
        for i in range(site_location_certainty):
            self.tableWidget_site_location_certainty.removeRow(0)
        #self.insert_new_row("self.tableWidget_site_location_certainty")
        for i in range(geometry_extent):
            self.tableWidget_geometry_extent.removeRow(0)
        #self.insert_new_row("self.tableWidget_geometry_extent")
        self.comboBox_site_overall_shape_type.setEditText('')
        self.comboBox_grid.setEditText('')  
        for i in range(country_type):
            self.tableWidget_country_type.removeRow(0)
        #self.insert_new_row("self.tableWidget_country_type")
        self.comboBox_cadastral_reference.setEditText('')  # 4 - comune
        self.comboBox_resource_orientation.setEditText('')  # 4 - comune
        self.comboBox_Address.setEditText('')  # 4 - comune
        self.comboBox_address_type.setEditText('')  # 4 - comune
        self.comboBox_administrative_subvision.setEditText('')  # 4 - comune
        self.comboBox_administrative_subvision_type.setEditText('') 
        for i in range(oac):
            self.tableWidget_overall_arch_cert.removeRow(0)
        #self.insert_new_row("self.tableWidget_overall_arch_cert")
        for i in range(osm):
            self.tableWidget_overall_site_morph.removeRow(0)        
        #self.insert_new_row("self.tableWidget_overall_site_morph")
        self.comboBox_cultural_period.setEditText('')
        for i in range(cpc):
            self.tableWidget_cultural_period_cert.removeRow(0)
        #self.insert_new_row("self.tableWidget_cultural_period_cert")
        for i in range(cspc):
            self.tableWidget_cultural_sub_period_cert.removeRow(0)
        #self.insert_new_row("self.tableWidget_cultural_sub_period_cert")
        for i in range(spc):
            self.tableWidget_sub_period_cert.removeRow(0)
        #self.insert_new_row("self.tableWidget_sub_period_cert")
        self.comboBox_date_inference.setEditText('')
        self.comboBox_arch_date.setEditText('')
        self.comboBox_arch_date_to.setEditText('')
        self.mDateEdit_9.clear()
        self.mDateEdit_10.clear()
        self.mDateEdit_11.clear()
        self.mDateEdit_12.clear()
        self.mDateEdit_13.clear()
        self.mDateEdit_14.clear()
        for i in range(sfft):
            self.tableWidget_site_features_from_type.removeRow(0)
        #self.insert_new_row("self.tableWidget_site_features_from_type")
        for i in range(sfftc):
            self.tableWidget_site_feature_from_type_cert.removeRow(0)
        #self.insert_new_row("self.tableWidget_site_feature_from_type_cert")
        for i in range(sfst):
            self.tableWidget_site_feature_shape_type.removeRow(0)
        #self.insert_new_row("self.tableWidget_site_feature_shape_type")
        for i in range(sfat):
            self.tableWidget_site_feature_arrangement_type.removeRow(0)
        #self.insert_new_row("self.tableWidget_site_feature_arrangement_type")
        for i in range(sfnt):
            self.tableWidget_site_feature_number_type.removeRow(0)
        #self.insert_new_row("self.tableWidget_site_feature_number_type")
        for i in range(sfit):
            self.tableWidget_site_feature_interpretation_type.removeRow(0)
        #self.insert_new_row("self.tableWidget_site_feature_interpretation_type")
        for i in range(sfin):
            self.tableWidget_site_feature_interpretation_number.removeRow(0)
        #self.insert_new_row("self.tableWidget_site_feature_interpretation_number")
        for i in range(sic):
            self.tableWidget_site_interpretation_cert.removeRow(0)
        #self.insert_new_row("self.tableWidget_site_interpretation_cert")
        for i in range(built):
            self.tableWidget_built.removeRow(0)
        #self.insert_new_row("self.tableWidget_built")
        for i in range(hpr):
            self.tableWidget_hp_related.removeRow(0)
        #self.insert_new_row("self.tableWidget_hp_related")
        self.comboBox_material_class.setEditText('')
        self.comboBox_material_type.setEditText('')
        self.comboBox_contruction_tech.setEditText('')
        self.comboBox_measurement_number.setEditText('')
        for i in range(mu):
            self.tableWidget_measurement_unit.removeRow(0)
        #self.insert_new_row("self.tableWidget_measurement_unit")
        for i in range(dt):
            self.tableWidget_dimension_type.removeRow(0)
        #self.insert_new_row("self.tableWidget_dimension_type")
        for i in range(mst):
            self.tableWidget_measurement_siurce_type.removeRow(0)       
        #self.insert_new_row("self.tableWidget_measurement_siurce_type")
        self.comboBox_related_geoarch.setEditText('')
        for i in range(overall_condition_state):
            self.tableWidget_overall_condition_state.removeRow(0)
        #self.insert_new_row("self.tableWidget_overall_condition_state")
        for i in range(damage):
            self.tableWidget_damage.removeRow(0)
        #self.insert_new_row("self.tableWidget_damage")
        self.comboBox_disturbance_cause_category.setEditText('')  # 4 - comune
        for i in range(disturbance_cause):
            self.tableWidget_disturbance_cause.removeRow(0)
        #self.insert_new_row("self.tableWidget_disturbance_cause")
        for i in range(disturbance_cause_2):
            self.tableWidget_disturbance_cause_2.removeRow(0)
        #self.insert_new_row("self.tableWidget_disturbance_cause_2")
        self.mDateEdit_5.clear()
        self.mDateEdit_6.clear()
        self.mDateEdit_7.clear()
        self.mDateEdit_8.clear()
        self.comboBox_disturbance_cause_ass.setEditText('')
        for i in range(effect_type):
            self.tableWidget_effect_type.removeRow(0)
        #self.insert_new_row("self.tableWidget_effect_type")
        for i in range(effect_certainty):
            self.tableWidget_effect_certainty.removeRow(0)
        #self.insert_new_row("self.tableWidget_effect_certainty")
        self.comboBox_threat_category.setEditText('')  # 4 - comune
        for i in range(threat_type):
            self.tableWidget_threat_type.removeRow(0)
        #self.insert_new_row("self.tableWidget_threat_type")
        for i in range(threat_probability):
            self.tableWidget_threat_probability.removeRow(0)
        #self.insert_new_row("self.tableWidget_threat_probability")
        self.comboBox_threat.setEditText('')  # 4 - comune
        self.comboBox_int_activity_type.setEditText('')  # 4 - comune
        self.comboBox_raccomandation.setEditText('')  # 4 - comune
        self.comboBox_priority.setEditText('')  # 4 - comune
        self.comboBox_related.setEditText('')  # 4 - comune
        for i in range(topography_type):
            self.tableWidget_topography_type.removeRow(0)            
        #self.insert_new_row("self.tableWidget_topography_type")
        self.comboBox_land_cover_type.setEditText('')  # 4 - comune
        self.comboBox_land_cover_assessment.setEditText('')  # 4 - comune
        self.comboBox_surficial.setEditText('')  # 4 - comune
        self.comboBox_depositional.setEditText('')  # 4 - comune
        self.comboBox_bedrock.setEditText('')  # 4 - comune
        self.comboBox_fetch.setEditText('')  # 4 - comune
        self.comboBox_wave.setEditText('')  # 4 - comune
        self.comboBox_tidal_energy.setEditText('')  # 4 - comune
        self.comboBox_depth_max.setEditText('')  # 4 - comune
        self.comboBox_depth_min.setEditText('')  # 4 - comune
        self.comboBox_datum_type.setEditText('')  # 4 - comune
        self.comboBox_datum_description.setEditText('')  # 4 - comune
        self.comboBox_restricted.setEditText('')  # 4 - comune
    
    
    def fill_fields(self, n=0):
        self.rec_num = n
        try:
            str(self.comboBox_location.setEditText(self.DATA_LIST[self.rec_num].location))  # 1 - Sito
            self.tableInsertData("self.tableWidget_investigator", self.DATA_LIST[self.rec_num].assessment_investigator_actor)
            self.tableInsertData("self.tableWidget_role", self.DATA_LIST[self.rec_num].investigator_role_type)
            self.tableInsertData("self.tableWidget_activity", self.DATA_LIST[self.rec_num].assessment_activity_type)
            self.tableInsertData("self.tableWidget_date_activity" , self.DATA_LIST[self.rec_num].assessment_activity_date)
            str(self.comboBox_ge_assessment.setEditText(self.DATA_LIST[self.rec_num].ge_assessment))
            self.mDateEdit_1.setText(self.DATA_LIST[self.rec_num].ge_imagery_acquisition_date) 
            str(self.comboBox_information_resource_used.setEditText(self.DATA_LIST[self.rec_num].information_resource_used)) 
            self.mDateEdit_2.setText(self.DATA_LIST[self.rec_num].information_resource_acquisition_date) # 8 - path
            str(self.comboBox_name_site.setEditText(self.DATA_LIST[self.rec_num].resource_name))  
            str(self.comboBox_resource_type.setEditText(self.DATA_LIST[self.rec_num].name_type))  
            self.tableInsertData("self.tableWidget_hplacetype", self.DATA_LIST[self.rec_num].heritage_place_type)
            str(self.comboBox_general_description_type.setEditText(self.DATA_LIST[self.rec_num].general_description_type)) 
            str(self.textEdit_general_description.setText(self.DATA_LIST[self.rec_num].general_description))  
            self.tableInsertData("self.tableWidget_hplacefuntion", self.DATA_LIST[self.rec_num].heritage_place_function)
            self.tableInsertData("self.tableWidget_hplacefunctioncertainty", self.DATA_LIST[self.rec_num].heritage_place_function_certainty)
            str(self.comboBox_designation.setEditText(self.DATA_LIST[self.rec_num].designation))
            self.mDateEdit_3.setText(self.DATA_LIST[self.rec_num].designation_from_date) 
            self.mDateEdit_4.setText(self.DATA_LIST[self.rec_num].designation_to_date)
            self.tableInsertData("self.tableWidget_geometry_place", self.DATA_LIST[self.rec_num].geometric_place_expression)
            str(self.comboBox_geometry_qualifier.setEditText(self.DATA_LIST[self.rec_num].geometry_qualifier))  
            self.tableInsertData("self.tableWidget_site_location_certainty", self.DATA_LIST[self.rec_num].site_location_certainty)
            self.tableInsertData("self.tableWidget_geometry_extent", self.DATA_LIST[self.rec_num].geometry_extent_certainty)
            str(self.comboBox_site_overall_shape_type.setEditText(self.DATA_LIST[self.rec_num].site_overall_shape_type))
            str(self.comboBox_grid.setEditText(self.DATA_LIST[self.rec_num].grid_id))  
            self.tableInsertData("self.tableWidget_country_type", self.DATA_LIST[self.rec_num].country_type)
            str(self.comboBox_cadastral_reference.setEditText(self.DATA_LIST[self.rec_num].cadastral_reference))  # 4 - comune
            str(self.comboBox_resource_orientation.setEditText(self.DATA_LIST[self.rec_num].resource_orientation))  # 4 - comune
            str(self.comboBox_Address.setEditText(self.DATA_LIST[self.rec_num].address))  # 4 - comune
            str(self.comboBox_address_type.setEditText(self.DATA_LIST[self.rec_num].address_type))  # 4 - comune
            str(self.comboBox_administrative_subvision.setEditText(self.DATA_LIST[self.rec_num].administrative_subdivision))  # 4 - comune
            str(self.comboBox_administrative_subvision_type.setEditText(self.DATA_LIST[self.rec_num].administrative_subdivision_type)) 
            self.tableInsertData("self.tableWidget_overall_arch_cert", self.DATA_LIST[self.rec_num].overall_archaeological_certainty_value)
            self.tableInsertData("self.tableWidget_overall_site_morph", self.DATA_LIST[self.rec_num].overall_site_morphology_type)
            str(self.comboBox_cultural_period.setEditText(self.DATA_LIST[self.rec_num].cultural_period_type))
            self.tableInsertData("self.tableWidget_cultural_period_cert", self.DATA_LIST[self.rec_num].cultural_period_certainty)
            self.tableInsertData("self.tableWidget_cultural_sub_period_cert", self.DATA_LIST[self.rec_num].cultural_subperiod_type)
            self.tableInsertData("self.tableWidget_sub_period_cert", self.DATA_LIST[self.rec_num].cultural_subperiod_certainty)
            str(self.comboBox_date_inference.setEditText(self.DATA_LIST[self.rec_num].date_inference_making_actor))
            str(self.comboBox_arch_date.setEditText(self.DATA_LIST[self.rec_num].archaeological_date_from))
            str(self.comboBox_arch_date_to.setEditText(self.DATA_LIST[self.rec_num].archaeological_date_to))
            self.mDateEdit_9.setText(self.DATA_LIST[self.rec_num].bp_date_from)
            self.mDateEdit_10.setText(self.DATA_LIST[self.rec_num].bp_date_to)
            self.mDateEdit_11.setText(self.DATA_LIST[self.rec_num].ah_date_from)
            self.mDateEdit_12.setText(self.DATA_LIST[self.rec_num].ah_date_to)
            self.mDateEdit_13.setText(self.DATA_LIST[self.rec_num].sh_date_from)
            self.mDateEdit_14.setText(self.DATA_LIST[self.rec_num].sh_date_to)
            self.tableInsertData("self.tableWidget_site_features_from_type", self.DATA_LIST[self.rec_num].site_feature_form_type)
            self.tableInsertData("self.tableWidget_site_feature_from_type_cert", self.DATA_LIST[self.rec_num].site_feature_form_type_certainty)
            self.tableInsertData("self.tableWidget_site_feature_shape_type", self.DATA_LIST[self.rec_num].site_feature_shape_type)
            self.tableInsertData("self.tableWidget_site_feature_arrangement_type", self.DATA_LIST[self.rec_num].site_feature_arrangement_type)
            self.tableInsertData("self.tableWidget_site_feature_number_type", self.DATA_LIST[self.rec_num].site_feature_number_type)
            self.tableInsertData("self.tableWidget_site_feature_interpretation_type", self.DATA_LIST[self.rec_num].site_feature_interpretation_type)
            self.tableInsertData("self.tableWidget_site_feature_interpretation_number", self.DATA_LIST[self.rec_num].site_feature_interpretation_number)
            self.tableInsertData("self.tableWidget_site_interpretation_cert", self.DATA_LIST[self.rec_num].site_feature_interpretation_certainty)
            self.tableInsertData("self.tableWidget_built", self.DATA_LIST[self.rec_num].built_component_related_resource)
            self.tableInsertData("self.tableWidget_hp_related", self.DATA_LIST[self.rec_num].hp_related_resource)
            str(self.comboBox_material_class.setEditText(self.DATA_LIST[self.rec_num].material_class))
            str(self.comboBox_material_type.setEditText(self.DATA_LIST[self.rec_num].material_type))
            str(self.comboBox_contruction_tech.setEditText(self.DATA_LIST[self.rec_num].construction_technique))
            str(self.comboBox_measurement_number.setEditText(self.DATA_LIST[self.rec_num].measurement_number))
            self.tableInsertData("self.tableWidget_measurement_unit", self.DATA_LIST[self.rec_num].measurement_unit) 
            self.tableInsertData("self.tableWidget_dimension_type", self.DATA_LIST[self.rec_num].dimension_type) 
            self.tableInsertData("self.tableWidget_measurement_siurce_type", self.DATA_LIST[self.rec_num].measurement_source_type)   
            str(self.comboBox_related_geoarch.setEditText(self.DATA_LIST[self.rec_num].related_geoarch_palaeo))
            self.tableInsertData("self.tableWidget_overall_condition_state", self.DATA_LIST[self.rec_num].overall_condition_state)
            self.tableInsertData("self.tableWidget_damage", self.DATA_LIST[self.rec_num].damage_extent_type)
            str(self.comboBox_disturbance_cause_category.setEditText(self.DATA_LIST[self.rec_num].disturbance_cause_category_type))  # 4 - comune
            self.tableInsertData("self.tableWidget_disturbance_cause", self.DATA_LIST[self.rec_num].disturbance_cause_type)
            self.tableInsertData("self.tableWidget_disturbance_cause_2", self.DATA_LIST[self.rec_num].disturbance_cause_certainty)
            self.mDateEdit_5.setText(self.DATA_LIST[self.rec_num].disturbance_date_from)
            self.mDateEdit_6.setText(self.DATA_LIST[self.rec_num].disturbance_date_to)
            self.mDateEdit_7.setText(self.DATA_LIST[self.rec_num].disturbance_date_occurred_before)
            self.mDateEdit_8.setText(self.DATA_LIST[self.rec_num].disturbance_date_occurred_on)
            str(self.comboBox_disturbance_cause_ass.setEditText(self.DATA_LIST[self.rec_num].disturbance_cause_assignment_assessor_name))
            self.tableInsertData("self.tableWidget_effect_type", self.DATA_LIST[self.rec_num].effect_type)
            self.tableInsertData("self.tableWidget_effect_certainty", self.DATA_LIST[self.rec_num].effect_certainty)
            str(self.comboBox_threat_category.setEditText(self.DATA_LIST[self.rec_num].threat_category))  # 4 - comune
            self.tableInsertData("self.tableWidget_threat_type", self.DATA_LIST[self.rec_num].threat_type)
            self.tableInsertData("self.tableWidget_threat_probability", self.DATA_LIST[self.rec_num].threat_probability)
            str(self.comboBox_threat.setEditText(self.DATA_LIST[self.rec_num].threat_inference_making_assessor_name))  # 4 - comune
            str(self.comboBox_int_activity_type.setEditText(self.DATA_LIST[self.rec_num].intervention_activity_type))  # 4 - comune
            str(self.comboBox_raccomandation.setEditText(self.DATA_LIST[self.rec_num].recommendation_type))  # 4 - comune
            str(self.comboBox_priority.setEditText(self.DATA_LIST[self.rec_num].priority_type))  # 4 - comune
            str(self.comboBox_related.setEditText(self.DATA_LIST[self.rec_num].related_detailed_condition_resource))  # 4 - comune
            self.tableInsertData("self.tableWidget_topography_type", self.DATA_LIST[self.rec_num].topography_type)
            str(self.comboBox_land_cover_type.setEditText(self.DATA_LIST[self.rec_num].land_cover_type))  # 4 - comune
            str(self.comboBox_land_cover_assessment.setEditText(self.DATA_LIST[self.rec_num].land_cover_assessment_date))  # 4 - comune
            str(self.comboBox_surficial.setEditText(self.DATA_LIST[self.rec_num].surficial_geology_type))  # 4 - comune
            str(self.comboBox_depositional.setEditText(self.DATA_LIST[self.rec_num].depositional_process))  # 4 - comune
            str(self.comboBox_bedrock.setEditText(self.DATA_LIST[self.rec_num].bedrock_geology))  # 4 - comune
            str(self.comboBox_fetch.setEditText(self.DATA_LIST[self.rec_num].fetch_type))  # 4 - comune
            str(self.comboBox_wave.setEditText(self.DATA_LIST[self.rec_num].wave_climate))  # 4 - comune
            str(self.comboBox_tidal_energy.setEditText(self.DATA_LIST[self.rec_num].tidal_energy))  # 4 - comune
            str(self.comboBox_depth_max.setEditText(self.DATA_LIST[self.rec_num].minimum_depth_max_elevation))  # 4 - comune
            str(self.comboBox_depth_min.setEditText(self.DATA_LIST[self.rec_num].maximum_depth_min_elevation))  # 4 - comune
            str(self.comboBox_datum_type.setEditText(self.DATA_LIST[self.rec_num].datum_type))  # 4 - comune
            str(self.comboBox_datum_description.setEditText(self.DATA_LIST[self.rec_num].datum_description_epsg_code))  # 4 - comune
            str(self.comboBox_restricted.setEditText(self.DATA_LIST[self.rec_num].restricted_access_record_designation))
        except:# AssertionError as e:
            pass#QMessageBox.warning(self, "Message",str(e), QMessageBox.Ok)
    
    
    
    
    def set_rec_counter(self, t, c):
        self.rec_tot = t
        self.rec_corr = c
        self.label_rec_tot.setText(str(self.rec_tot))
        self.label_rec_corrente.setText(str(self.rec_corr))
    def set_LIST_REC_TEMP(self):
        
        role= self.table2dict("self.tableWidget_role")
        activity= self.table2dict("self.tableWidget_activity")
        investigator= self.table2dict("self.tableWidget_investigator")
        date_activity= self.table2dict("self.tableWidget_date_activity") 
        hplacetype= self.table2dict("self.tableWidget_hplacetype") 
        hplacefuntion= self.table2dict("self.tableWidget_hplacefuntion") 
        hplacefunctioncertainty= self.table2dict("self.tableWidget_hplacefunctioncertainty") 
        geometry_place= self.table2dict("self.tableWidget_geometry_place") 
        site_location_certainty= self.table2dict("self.tableWidget_site_location_certainty") 
        geometry_extent= self.table2dict("self.tableWidget_geometry_extent") 
        country_type= self.table2dict("self.tableWidget_country_type") 
        overall_condition_state = self.table2dict("self.tableWidget_overall_condition_state") 
        damage= self.table2dict("self.tableWidget_damage") 
        disturbance_cause= self.table2dict("self.tableWidget_disturbance_cause") 
        disturbance_cause_2= self.table2dict("self.tableWidget_disturbance_cause_2") 
        effect_type= self.table2dict("self.tableWidget_effect_type") 
        effect_certainty= self.table2dict("self.tableWidget_effect_certainty") 
        threat_type= self.table2dict("self.tableWidget_threat_type") 
        threat_probability= self.table2dict("self.tableWidget_threat_probability") 
        topography_type= self.table2dict("self.tableWidget_topography_type") 
        oac=  self.table2dict("self.tableWidget_overall_arch_cert")
        osm=  self.table2dict("self.tableWidget_overall_site_morph")
        cpc=  self.table2dict("self.tableWidget_cultural_period_cert")
        cspc= self.table2dict("self.tableWidget_cultural_sub_period_cert")
        spc=   self.table2dict("self.tableWidget_sub_period_cert")
        sfft=  self.table2dict("self.tableWidget_site_features_from_type")
        sfftc= self.table2dict("self.tableWidget_site_feature_from_type_cert")
        sfst=  self.table2dict("self.tableWidget_site_feature_shape_type")
        sfat=  self.table2dict("self.tableWidget_site_feature_arrangement_type")
        sfnt=  self.table2dict("self.tableWidget_site_feature_number_type")
        sfit=  self.table2dict("self.tableWidget_site_feature_interpretation_type")
        sfin=  self.table2dict("self.tableWidget_site_feature_interpretation_number")
        sic=   self.table2dict("self.tableWidget_site_interpretation_cert")
        built= self.table2dict("self.tableWidget_built")
        hpr=    self.table2dict("self.tableWidget_hp_related")
        mu=  self.table2dict("self.tableWidget_measurement_unit")
        dt=  self.table2dict("self.tableWidget_dimension_type")
        mst= self.table2dict("self.tableWidget_measurement_siurce_type")
        self.DATA_LIST_REC_TEMP = [
            str(self.comboBox_location.currentText()),  # 1 - Sito
            str(investigator),
            str(role),
            str(activity),
            str(date_activity),
            str(self.comboBox_ge_assessment.currentText()),  # 3 - regione
            str(self.mDateEdit_1.text()), # 8 - path
            str(self.comboBox_information_resource_used.currentText()),  # 3 - regione
            str(self.mDateEdit_2.text()), # 8 - path
            str(self.comboBox_name_site.currentText()),  
            str(self.comboBox_resource_type.currentText()),  
            str(hplacetype),
            str(self.comboBox_general_description_type.currentText()), 
            str(self.textEdit_general_description.toPlainText()),  
            str(hplacefuntion),
            str(hplacefunctioncertainty),
            str(self.comboBox_designation.currentText()),
            str(self.mDateEdit_3.text()), 
            str(self.mDateEdit_4.text()),
            str(geometry_place),
            str(self.comboBox_geometry_qualifier.currentText()),  
            str(site_location_certainty),
            str(geometry_extent),
            str(self.comboBox_site_overall_shape_type.currentText()),
            str(self.comboBox_grid.currentText()),  
            str(country_type),
            str(self.comboBox_cadastral_reference.currentText()),  # 4 - comune
            str(self.comboBox_resource_orientation.currentText()),  # 4 - comune
            str(self.comboBox_Address.currentText()),  # 4 - comune
            str(self.comboBox_address_type.currentText()),  # 4 - comune
            str(self.comboBox_administrative_subvision.currentText()),  # 4 - comune
            str(self.comboBox_administrative_subvision_type.currentText()), 
            str(oac),
            str(osm),
            str(self.comboBox_cultural_period.currentText()),
            str(cpc),
            str(cspc),
            str(spc),
            str(self.comboBox_date_inference.currentText()),
            str(self.comboBox_arch_date.currentText()),
            str(self.comboBox_arch_date_to.currentText()),
            str(self.mDateEdit_9.text()),
            str(self.mDateEdit_10.text()),
            str(self.mDateEdit_11.text()),
            str(self.mDateEdit_12.text()),
            str(self.mDateEdit_13.text()),
            str(self.mDateEdit_14.text()),
            str(sfft),
            str(sfftc),
            str(sfst),
            str(sfat),
            str(sfnt),
            str(sfit),
            str(sfin),
            str(sic),
            str(built),
            str(hpr),
            str(self.comboBox_material_class.currentText()),
            str(self.comboBox_material_type.currentText()),
            str(self.comboBox_contruction_tech.currentText()),
            str(self.comboBox_measurement_number.currentText()),
            str(mu), 
            str(dt), 
            str(mst),        
            str(self.comboBox_related_geoarch.currentText()),
            str(overall_condition_state),
            str(damage),
            str(self.comboBox_disturbance_cause_category.currentText()),  # 4 - comune
            str(disturbance_cause),
            str(disturbance_cause_2),
            str(self.mDateEdit_5.text()),
            str(self.mDateEdit_6.text()),
            str(self.mDateEdit_7.text()),
            str(self.mDateEdit_8.text()),
            str(self.comboBox_disturbance_cause_ass.currentText()),
            str(effect_type),
            str(effect_certainty),
            str(self.comboBox_threat_category.currentText()),  # 4 - comune
            str(threat_type),
            str(threat_probability),
            str(self.comboBox_threat.currentText()),  # 4 - comune
            str(self.comboBox_int_activity_type.currentText()),  # 4 - comune
            str(self.comboBox_raccomandation.currentText()),  # 4 - comune
            str(self.comboBox_priority.currentText()),  # 4 - comune
            str(self.comboBox_related.currentText()),  # 4 - comune
            str(topography_type),
            str(self.comboBox_land_cover_type.currentText()),  # 4 - comune
            str(self.comboBox_land_cover_assessment.currentText()),  # 4 - comune
            str(self.comboBox_surficial.currentText()),  # 4 - comune
            str(self.comboBox_depositional.currentText()),  # 4 - comune
            str(self.comboBox_bedrock.currentText()),  # 4 - comune
            str(self.comboBox_fetch.currentText()),  # 4 - comune
            str(self.comboBox_wave.currentText()),  # 4 - comune
            str(self.comboBox_tidal_energy.currentText()),  # 4 - comune
            str(self.comboBox_depth_max.currentText()),  # 4 - comune
            str(self.comboBox_depth_min.currentText()),  # 4 - comune
            str(self.comboBox_datum_type.currentText()),  # 4 - comune
            str(self.comboBox_datum_description.currentText()),  # 4 - comune
            str(self.comboBox_restricted.currentText())]
    def set_LIST_REC_CORR(self):
        self.DATA_LIST_REC_CORR = []
        for i in self.TABLE_FIELDS:
            self.DATA_LIST_REC_CORR.append(eval("str(self.DATA_LIST[self.REC_CORR]." + i + ")"))
    def setComboBoxEnable(self, f, v):
        field_names = f
        value = v
        for fn in field_names:
            cmd = '{}{}{}{}'.format(fn, '.setEnabled(', v, ')')
            eval(cmd)
    def setComboBoxEditable(self, f, n):
        field_names = f
        value = n
        for fn in field_names:
            cmd = '{}{}{}{}'.format(fn, '.setEditable(', n, ')')
            eval(cmd)
    def rec_toupdate(self):
        rec_to_update = self.UTILITY.pos_none_in_list(self.DATA_LIST_REC_TEMP)
        return rec_to_update
    def records_equal_check(self):
        self.set_LIST_REC_TEMP()
        self.set_LIST_REC_CORR()
        if self.DATA_LIST_REC_CORR == self.DATA_LIST_REC_TEMP:
            return 0
        else:
            return 1
    def update_record(self):
        try:
            self.DB_MANAGER.update(self.MAPPER_TABLE_CLASS,
                                   self.ID_TABLE,
                                   [eval("int(self.DATA_LIST[self.REC_CORR]." + self.ID_TABLE + ")")],
                                   self.TABLE_FIELDS,
                                   self.rec_toupdate())
            return 1
        except Exception as e:
            QMessageBox.warning(self, "Message",
                                "encoding problem: accents or characters not accepted by the database have been inserted. If you close the card now without correcting the errors you will lose the data. Make a copy of everything on a separate word sheet. Error :" + str(
                                    e), QMessageBox.Ok)
            return 0
    def list2pipe(self,x):
        lista =[]
        if isinstance(x,str) and x.startswith('[') and '], [' in x:
            
            return '|'.join(str(e) for e in eval(x)).replace("['",'').replace("']",'').replace("[",'').replace("]",'')
            
        elif isinstance(x,str) and x.startswith('[['):    
            return '|'.join(str(e) for e in eval(x)[0])
       
        elif isinstance(x,str) and x.startswith('[]'): 
            return ''
        
        else: 
            return x
    def load_spatialite(self,conn, connection_record):
        conn.enable_load_extension(True)
        if Hff_OS_Utility.isWindows()== True:
            conn.load_extension('mod_spatialite.dll')
        elif Hff_OS_Utility.isMac()== True:
            conn.load_extension('mod_spatialite.dylib')
        else:
            conn.load_extension('mod_spatialite.so')  
    
    def on_pushButton_export_excel_pressed(self):
        home = os.environ['HFF_HOME']
        sito_path = '{}{}{}'.format(self.HOME, os.sep, "HFF_EXCEL_folder")
        sito_location = str(self.comboBox_location.currentText())
        cfg_rel_path = os.path.join(os.sep, 'HFF_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(home, cfg_rel_path)
        conf = open(file_path, "r")
        data = conf.read()
        settings = Settings(data)
        settings.set_configuration()
        conf.close()    
        
        db_username = settings.USER
        host = settings.HOST
        port = settings.PORT
        database_password=settings.PASSWORD
        db_names = settings.DATABASE
        server=settings.SERVER    
        
        
        if server=='sqlite':        
            
            self.HOME = os.environ['HFF_HOME']
            sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,"HFF_DB_folder")
            
            file_path_sqlite = sqlite_DB_path+os.sep+db_names
            conn = sq.connect(file_path_sqlite)
            conn.enable_load_extension(True)
            
            conn.execute('SELECT load_extension("mod_spatialite")')   
            conn.execute('SELECT InitSpatialMetaData(1);')  
            
            cur1 = conn.cursor()
            
            name_= '%s' % (sito_location+'_site-table_' +  time.strftime('%Y%m%d_') + '.xlsx')
            dump_dir=os.path.join(sito_path, name_)
            writer = pd.ExcelWriter(dump_dir, engine='xlsxwriter')
            workbook  = writer.book
            
            cur1.execute("Select Distinct location, assessment_investigator_actor, investigator_role_type, assessment_activity_type, assessment_activity_date, ge_assessment, ge_imagery_acquisition_date, information_resource_used, information_resource_acquisition_date, resource_name, name_type, heritage_place_type, general_description_type, general_description, heritage_place_function, heritage_place_function_certainty, designation, designation_from_date, designation_to_date, geometric_place_expression, geometry_qualifier, site_location_certainty, geometry_extent_certainty, site_overall_shape_type, grid_id, country_type, cadastral_reference, resource_orientation, address, address_type, administrative_subdivision, administrative_subdivision_type, overall_archaeological_certainty_value, overall_site_morphology_type, cultural_period_type, cultural_period_certainty, cultural_subperiod_type, cultural_subperiod_certainty, date_inference_making_actor, archaeological_date_from, archaeological_date_to, bp_date_from, bp_date_to, ah_date_from, ah_date_to, sh_date_from, sh_date_to, site_feature_form_type, site_feature_form_type_certainty, site_feature_shape_type, site_feature_arrangement_type, site_feature_number_type, site_feature_interpretation_type, site_feature_interpretation_number, site_feature_interpretation_certainty, built_component_related_resource, hp_related_resource, material_class, material_type, construction_technique, measurement_number, measurement_unit, dimension_type, measurement_source_type, related_geoarch_palaeo, overall_condition_state, damage_extent_type, disturbance_cause_category_type, disturbance_cause_type, disturbance_cause_certainty, disturbance_date_from, disturbance_date_to, disturbance_date_occurred_before, disturbance_date_occurred_on, disturbance_cause_assignment_assessor_name, effect_type, effect_certainty, threat_category, threat_type, threat_probability, threat_inference_making_assessor_name, intervention_activity_type, recommendation_type, priority_type, related_detailed_condition_resource, topography_type, land_cover_type, land_cover_assessment_date, surficial_geology_type, depositional_process, bedrock_geology, fetch_type, wave_climate, tidal_energy, minimum_depth_max_elevation, maximum_depth_min_elevation, datum_type, datum_description_epsg_code, restricted_access_record_designation from eamena_table  where location= '%s'" %sito_location)
            rows1 = cur1.fetchall()
            
            
            
            col_names0 =['ASSESSMENT SUMMARY','RESOURCE SUMMARY','GEOMETRIES,GEOGRAPHY','ARCHAEOLOGICAL ASSESSMENT','CONDITION ASSESSMENT','ENVIRONMENT ASSESSMENT','ACCESS']
            
            
            col_names1 =['UNIQUEID','Assessment Investigator - Actor','Investigator Role Type','Assessment Activity Type','Assessment Activity Date','GE Assessment(Yes/No)','GE Imagery Acquisition Date','Information Resource Used','Information Resource Acquisition Date','Resource Name','Name Type','Heritage Place Type','General Description Type','General Description','Heritage Place Function','Heritage Place Function Certainty','Designation','Designation From Date','Designation To Date','Geometric Place Expression','Geometry Qualifier','Site Location Certainty','Geometry Extent Certainty','Site Overall Shape Type','Grid ID','Country Type','Cadastral Reference','Resource Orientation','Address','Address Type','Administrative Subdivision','Administrative Subdivision Type','Overall Archaeological Certainty Value','Overall Site Morphology Type','Cultural Period Type','Cultural Period Certainty','Cultural Subperiod Type','Cultural Subperiod Certainty','Date Inference Making Actor','Archaeological Date From (cal)','Archaeological Date to (cal)','BP Date From','BP Date To','AH Date From','AH Date To','SH Date From','SH Date To','Site Feature Form Type','Site Feature Form Type Certainty','Site Feature Shape Type','Site Feature Arrangement Type','Site Feature Number Type','Site Feature Interpretation Type ','Site Feature Interpretation Number','Site Feature Interpretation Certainty','Built Component Related Resource','HP Related Resource','Material Class','Material Type','Construction Technique','Measurement Number','Measurement Unit','Dimension Type','Measurement Source Type','Related Geoarch/Palaeo','Overall Condition State','Damage Extent Type','Disturbance Cause Category Type','Disturbance Cause Type','Disturbance Cause Certainty','Disturbance Date From','Disturbance Date To','Disturbance Date Occurred Before','Disturbance Date Occurred On','Disturbance Cause Assignment Assessor Name','Effect Type','Effect Certainty','Threat Category','Threat Type','Threat Probability','Threat Inference Making Assessor Name','Intervention Activity Type','Recommendation Type','Priority Type','Related Detailed Condition Resource','Topography Type','Land Cover Type','Land Cover Assessment Date','Surficial Geology Type','Depositional Process','Bedrock Geology','Fetch Type','Wave Climate','Tidal Energy','Minimum Depth/Max Elevation(m)','Maximum Depth/Min Elevation(m)','Datum Type','Datum Description/EPSG code','Restricted Access Record Designation']
            
            
            
            t0=pd.DataFrame(rows1,columns=col_names1).applymap(self.list2pipe)
            format = workbook.add_format({'text_wrap': True, 'valign': 'top'})
            neutro_format = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#FDE9D9'})
            
            # Create a format to use in the merged range FIRST ROW.
            
            merge_format1 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#FDE9D9'})
                
            merge_format2 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#E4DFEC'})

            merge_format3 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#B7DEE8'})   
            
            merge_format4 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#DAEEF3'})   
            merge_format5 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#FFC5E7'})   
            merge_format6 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#DA9694'})   
            merge_format7 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#FCD5B4'})   
            
            merge_format8 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#FFC7CE'})
            
            ###################MERGE FORMA SECOND ROW#####################
            merge_format11 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#F2DCDB'})
                
            merge_format21 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#F79646'})

            merge_format31 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#B7DEE8'})   
            
            merge_format41 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#D8E4BC'})   
            merge_format51 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#FDE9D9'})   
            merge_format61 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#E6B8B7'})   
            merge_format71 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#FCD5B4'})   
            
            merge_format81 = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#C0504D'})
            # t0.columns = pd.MultiIndex.from_tuples(zip("0ciaomjkyftgdytrdfy0"),"000000000000000000000","0000000000000000000000","0000000000000000","0000000000000"), t0.columns)
           
            
            t0.to_excel(writer, sheet_name='Heritage Place',index=False, startrow=2)
            
            
            worksheet1 = writer.sheets['Heritage Place']
            
            worksheet1.set_column('A:S', 35, format)
            worksheet1.set_column('T:T', 100, format)
            worksheet1.set_column('U:CU', 35, format)
            
            
            
            ############first row####################
            worksheet1.merge_range('B1:I1','ASSESSMENT SUMMARY', merge_format1)
            worksheet1.merge_range('J1:S1','RESOURCE SUMMARY', merge_format2)
            worksheet1.merge_range('T1:W1','GEOMETRIES', merge_format3)
            worksheet1.merge_range('X1:AF1','GEOGRAPHY', merge_format4)
            worksheet1.merge_range('AG1:BM1','ARCHAEOLOGICAL ASSESSMENT', merge_format5)
            worksheet1.merge_range('BN1:CG1','CONDITION ASSESSMENT', merge_format6)
            worksheet1.merge_range('CH1:CT1','ENVIRONMENT ASSESSMENT', merge_format7)
            worksheet1.merge_range('CU1:CU2','ACCESS', merge_format8)
            #######secon row################################
            
            
            worksheet1.merge_range('D2:I2','ASSESSMENT ACTIVITY', merge_format11)
            worksheet1.merge_range('J2:K2','RESOURCE NAME', merge_format21)
            worksheet1.merge_range('M2:N2','RESOURCE DESCRIPTION', merge_format31)
            worksheet1.merge_range('O2:P2','HERITAGE RESOURCE CLASSIFICATION', merge_format41)
            worksheet1.merge_range('Q2:S2','DESIGNATION', merge_format51)
            worksheet1.merge_range('AC2:AD2','ADDRESS', merge_format61)
            worksheet1.merge_range('AE2:AF2','ADMINISTRATIVE SUBDIVISION', merge_format71)
            worksheet1.merge_range('AI2:AM2','PERIODIZATION', merge_format81)
            
            worksheet1.merge_range('AN2:AU2','ABSOLUTE CHRONOLOGY', merge_format11)
            worksheet1.merge_range('AV2:BE2','SITE FEATURES & INTERPRETATIONS', merge_format21)
            worksheet1.merge_range('BF2:BH2','MATERIAL', merge_format31)
            worksheet1.merge_range('BI2:BL2','MEASUREMENTS', merge_format41)
            worksheet1.merge_range('BP2:BY2','DISTURBANCES', merge_format51)
            worksheet1.merge_range('BZ2:CC2','THREATS', merge_format61)
            worksheet1.merge_range('CD2:CF2','RECOMMENDATION PLAN', merge_format71)
            
            worksheet1.merge_range('CI2:CJ2','LAND COVER', merge_format81)
            worksheet1.merge_range('CK2:CL2','SURFICIAL GEOLOGY', merge_format11)
            worksheet1.merge_range('CN2:CP2','MARINE ENVIRONMENT', merge_format21)
            worksheet1.merge_range('CQ2:CT2','DEPTH/ELEVATION', merge_format31)
            worksheet1.merge_range('B2:C2','', merge_format1)
            worksheet1.merge_range('L1:L2','', merge_format2)
            worksheet1.merge_range('T2:W2','', merge_format3)
            worksheet1.merge_range('X1:AB2','GEOGRAPHY', merge_format4)
            worksheet1.merge_range('AG1:AH2','ARCHAEOLOGICAL ASSESSMENT', merge_format5)
            worksheet1.merge_range('BM1:BM2','', merge_format5)
            worksheet1.merge_range('BN1:BO2','CONDITION ASSESSMENT', merge_format6)
            worksheet1.merge_range('CG1:CG2','', merge_format6)
            worksheet1.merge_range('CH1:CH2','ENVIRONMENT ASSESSMENT', merge_format7)
            worksheet1.merge_range('CM1:CM2','', merge_format7)
            
            
            
            
            writer.save()
        
            
        QMessageBox.warning(self, "Message","Exported completed" , QMessageBox.Ok)       
    def on_pushButton_open_dir_pressed(self):
        path = '{}{}{}'.format(self.HOME, os.sep, "HFF_EXCEL_folder")

        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
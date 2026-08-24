from time import sleep

from behave import *
from Bdd.page_obj.test_debug_page import NotePad
from autowork_core.page import get_page
from autowork_core.page import get_script_page

@when('For local debugging demo')
def test_bdd(context):
    ui = get_script_page(context,locator_files=['plan/window.yaml','plan/all_parameters_locator.yaml'])
    ui.wait_ready({'top_level':'true','class_name':'Notepad',"backend":'uia'},timeout=30)
    note = get_page(context,NotePad)
    note.test_click()

@when('For local debugging')
def test_bdd(context):
    sleep(10)



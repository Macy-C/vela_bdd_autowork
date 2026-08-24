from behave import given, then, when

from autowork_core.page import get_page
from Bdd.page_obj.notepad_file_menu.page import NotepadFileMenuPage
from Bdd.page_obj.notepad.page import NotepadPage


@given("新建标签页")
def given_new_tab(context):
    page = get_page(context, NotepadPage)
    page.click("$loc:file_menu")
    file_menu = get_page(context, NotepadFileMenuPage)
    file_menu.click("$loc:new_tab")


@given("设置字体加粗")
def given_bold_font(context):
    page = get_page(context, NotepadPage)
    page.click("$loc:bold_button")


@given("设置字体斜体")
def given_italic_font(context):
    page = get_page(context, NotepadPage)
    page.click("$loc:italic_button")


@when("输入 123456")
def when_input_123456(context):
    page = get_page(context, NotepadPage)
    page.click("$loc:notepad_editor", 363, 47)
    page.input_text("$loc:notepad_editor", "123456")


@when("删除34")
def when_delete_34(context):
    page = get_page(context, NotepadPage)
    page.click("$loc:notepad_editor", 59, 27)
    page.send_text_keys("$loc:notepad_editor", "{BACK}{BACK}")


@then("应该显示1256")
def then_should_display_1256(context):
    page = get_page(context, NotepadPage)
    page.assert_text_equal("$loc:notepad_editor", "1256")
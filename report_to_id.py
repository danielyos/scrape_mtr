from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import selenium.webdriver.support.expected_conditions as expected_conditions
from itertools import chain
import json
from selenium.webdriver.support.ui import Select

def tuition(driver):
    WebDriverWait(driver, 10).until(
        expected_conditions.presence_of_element_located((By.ID, "ctl00_Main_LblMehushav")))
    oz_tuition_item = driver.find_element_by_id("ctl00_Main_LblMehushav")
    return oz_tuition_item.text


def find_sum(driver, tr_name, td_location):
    elements = driver.find_elements_by_css_selector(tr_name)
    return elements[-1].find_elements_by_tag_name("td")[td_location].text


report_to_handler = {"שכר לימוד": tuition}
report_to_identifiers = {"תוספות למוסדות (מוכרים)": ("tr.EduGridViewRowGainsboro", 1),
                         "ידניים": ("tr.EduGridViewRowGainsboro", 1),
                         "שעורי עזר לעולים": ("tr.EduGridViewRowGainsboro", 1),
                         "סיכום מוסדות למוטב": ('tr.EduGridViewRow', 4),
                         "שרתים ומזכירים":('tr.EduGridViewRowGainsboro2', 1),
                         "תוספות למוטבים": ('tr.EduGridViewRowGainsboro', 1),
                         'גנ"י - גננות': ("tr.EduGridViewRowGainsboro", 1),
                         'גנ"י - עוזרות': ("tr.EduGridViewRowGainsboro", 1),
                         'גנ"י - שכל"מ': ("tr.EduGridViewRowGainsboro", 1),
                         'גנ"י - שכל"מ  מ. אזורית': ("tr.EduGridViewRowGainsboro", 1),
                         'הסעות כללי ': ("tr.EduGridViewAlternatingRowGainsboro", 2),
                         'הסעות נט': ("tr.EduGridViewRowGainsboro", 1),
                         'מועדוניות': ("tr.EduGridViewRowGainsboro", 1),

                         }


"""
    {"תוספות למוסדות (מוכרים)": ("tr.EduGridViewRowGainsboro", 1),
 "ידניים": ("tr.EduGridViewRowGainsboro", 1),
 "שעורי עזר לעולים": ("tr.EduGridViewRowGainsboro", 1)
"סיכום מוסדות למוטב": ('tr.EduGridViewRow', 4),
 'שכר לימוד חריגים': ('tr.EduGridViewRowGainsboro', 1),
 'שרתים ומזכירים': ('tr.EduGridViewRowGainsboro2', 1),
 'תוספות למוטבים': ('tr.EduGridViewRowGainsboro', 1)}




 }"""


def choose_institute(driver, type_of_institute):
    btn_name = 'ctl00_Main_rbtnMtv_1' if type_of_institute == 'mossad' else 'ctl00_Main_rbtnMtv_0'
    rb = WebDriverWait(driver, 10).until(
        expected_conditions.element_to_be_clickable((By.ID, btn_name)))
    rb.click()


def find_smalim(driver, type_of_institute):
    symbol_to_name = {}

    driver.get("http://apps.education.gov.il/mtrnet/home.aspx")
    sleep(2)
    choose_institute(driver, type_of_institute)
    search = WebDriverWait(driver, 10).until(expected_conditions.element_to_be_clickable((By.ID, "ctl00_Main_btnOK")))
    search.click()
    sleep(5)
    first_half_motavim = driver.find_elements_by_css_selector("tr.GridViewRow")
    second_half_motavim = driver.find_elements_by_css_selector("tr.GridViewAlternativeRow")

    for item in chain(first_half_motavim, second_half_motavim):
        data = item.text.split()
        if len(data) != 0:
            symbol_to_name[data[0]] = ' '.join(data[1:])
    return symbol_to_name

# specific report
def money_mossad(driver, num, type_of_institute):
    institution_reports = {}
    failed_reports = []
    ignored_reports = []

    driver.get("http://apps.education.gov.il/mtrnet/home.aspx")

    choose_institute(driver, type_of_institute)
    sleep(2)

    sml_tb = WebDriverWait(driver, 10).until(
        expected_conditions.visibility_of_element_located((By.NAME, "ctl00$Main$inpSml")))
    sml_tb.send_keys(num)

    search = WebDriverWait(driver, 10).until(expected_conditions.element_to_be_clickable((By.ID, "ctl00_Main_btnOK")))
    search.click()
    if type_of_institute == "mossad":
        row = WebDriverWait(driver, 10).until(
            expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="ctl00_Main_gvMsdList"]/tbody/tr[2]')))
    if type_of_institute == "mutav":
        row = WebDriverWait(driver, 10).until(
            expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="ctl00_Main_gvMtvList"]/tbody/tr[2]')))
    row.click()
    sleep(2)

    report_names = [report.text for report in Select(driver.find_element_by_id('ctl00_Main_ddlReports')).options]

    for report in report_names:
        report_options = Select(driver.find_element_by_id('ctl00_Main_ddlReports'))

        show_report = WebDriverWait(driver, 10).until(
            expected_conditions.element_to_be_clickable((By.ID, "ctl00_Main_btnOK")))

        if report in report_to_identifiers:
            report_options.select_by_visible_text(report)

            show_report.click()
            sleep(2)
            # value = report_to_handler[report](driver)
            try:
                value = find_sum(driver, *report_to_identifiers[report])
                institution_reports[report] = value
            except Exception:
                failed_reports.append(report)

            driver.back()

        else:
            ignored_reports.append(report)

    return institution_reports, failed_reports, ignored_reports


def main():
    results = {}
    driver = webdriver.Chrome()
    smalim = find_smalim(driver, 'mutav')
    for semel in smalim:
        results[semel] = money_mossad(driver, semel, "mutav")

        # if len(results) == 5:
        #     break

    with open("/tmp/lala1.json", 'w') as output:
        json.dump(results, output, ensure_ascii=False)

    results = {}

    smalim = find_smalim(driver, 'mossad')
    for semel in smalim:
        results[semel] = money_mossad(driver, semel, "mossad")
        #
        # if len(results) == 5:
        #     break

    with open("/tmp/lala.json", 'w') as output:
        json.dump(results, output, ensure_ascii=False)


if __name__ == "__main__":
    main()
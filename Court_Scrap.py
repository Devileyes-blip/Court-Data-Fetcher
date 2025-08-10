#  DRirect krr chorr get data aur ye sab 

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import streamlit as st
from PIL import Image
from io import BytesIO
import pandas as pd



st.title("Court-Data Fetcher")

success = (By.CSS_SELECTOR,  "div.alert.success_message.alert-success")
danger = (By.CSS_SELECTOR,  "div.alert.success_message.alert-danger")
if "stage" not in st.session_state:
    st.session_state.stage = "search"

if "page" not in st.session_state:
    st.session_state.page = "Page1"



if "driver" not in st.session_state:
    # chrome_options = Options()
    # chrome_options.add_argument("--headless")
    st.session_state.driver = webdriver.Chrome()
    st.session_state.driver.get("https://hcraj.nic.in/cishcraj-jp/")

driver = st.session_state.driver

if st.session_state.page == "Page1":

    checkbox_labels = ['Case/Reg. Type', 'Case/Reg. No', 'Filing Year']


    for i in  checkbox_labels:
        try:
            the_label = driver.find_element(By.XPATH, f"//label[contains(text(), '{i}')]")
            check_label = the_label.find_element(By.TAG_NAME, "input")

            if not check_label.is_selected():
                check_label.click()
                print("Checked")
        except Exception as e:
            print(f"Error: {e}")

    cl_of_case_type = driver.find_element(By.ID, "basetype")
    options = cl_of_case_type.find_elements(By.XPATH, "//option")
    case_categoryy = [j.text for j in options]
    case_category = st.selectbox("Case Category", case_categoryy[0:4])
    if case_category != "Select Category":
        #Case Type
        cl_of_case_type.click()
        cl_of_case_type.find_element(By.XPATH, f".//option[normalize-space()='{case_category}']").click()
        wait = WebDriverWait(driver, 10)
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#casetype option:first-child"), "All"))
        WebDriverWait(driver, 10)
        case_t = driver.find_element(By.ID, "casetype")
        case_ty = case_t.find_elements(By.XPATH, "./option")
        case_typ = [j.text for j in case_ty if j not in case_categoryy]
        case_type = st.selectbox("Case Type", case_typ)

        case_t.click()
        case_t.find_element(By.XPATH, f".//option[normalize-space()='{case_type}']").click()
        #Case  Number

            
        case_num = st.number_input("Case No", min_value = 1, step = 1)
        case_object =  driver.find_element(By.ID, "caseno")
        
        


        #Filing Year
        year = driver.find_element(By.ID, "diaryyr")
        year_drop_list = year.find_elements(By.XPATH, "./option")
        year_list = [j.text for j in year_drop_list]
        filing_year = st.selectbox("Filing Year", year_list)

        

        if "captcha_img" not in st.session_state:
            #Code to bypass captcha
            img_obj = driver.find_element(By.ID, "captcha")
            #Converted it into bytes and stored in  RAM like a file
            st.session_state.captcha_img  = img_obj.screenshot_as_png
        
        #CAPTCHA value
        st.image(st.session_state.captcha_img)
        cap_inp = st.text_input("Enter value of CAPTCHA", max_chars = 6)

        captcha_inp_obj = driver.find_element(By.ID, "txtCaptcha")
        

        if st.session_state.stage == "search":

                #Button to submit
            if st.button("Search"):
                if not cap_inp.isdigit():
                    st.error("Please enter valid CAPTCHA")
                else:
                    case_object.clear()
                    case_object.send_keys(str(case_num))

                    year.click()
                    year.find_element(By.XPATH, f".//option[normalize-space()='{filing_year}']").click()
                    
                    captcha_inp_obj.clear()
                    captcha_inp_obj.send_keys(cap_inp)

                    driver.find_element(By.ID, "btncasedetail1_1").click()
        
                    record_obj = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div.alert.success_message.alert-danger, div.alert.success_message.alert-success")))
                    text_record = WebDriverWait(driver, 10).until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, "div.alert.success_message.alert-danger, div.alert.success_message.alert-success"), " "))
                    if "Total " in record_obj.text:
                        st.success(record_obj.text)
                        img_obj = driver.find_element(By.ID, "captcha")
                        st.session_state.captcha_img = img_obj.screenshot_as_png
                        st.session_state.stage = "get_data"
                        st.rerun()
                    else:
                        st.error(record_obj.text)    
                        img_obj = driver.find_element(By.ID, "captcha")
                        st.session_state.captcha_img = img_obj.screenshot_as_png
                        st.rerun()                    
                    
        elif st.session_state.stage == "get_data":
            if st.button("Get Data"):
                if cap_inp.isdigit():
                    captcha_inp_obj.clear()
                    captcha_inp_obj.send_keys(cap_inp)
                    driver.find_element(By.ID, "btncasedetail1_2").click()
                    try:
                        record_obj = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div.alert.success_message.alert-danger")))
                        st.session_state.stage = "search"
                        img_obj = driver.find_element(By.ID, "captcha")
                        st.session_state.captcha_img = img_obj.screenshot_as_png
                        st.rerun()
                    except:
                        print("DO it")
                    st.session_state.page = "Page2"
                    st.rerun()
                else:
                    st.error("Please enter valid Captcha")
                    st.session_state.stage = "search"
                    st.rerun()
elif st.session_state.page == "Page2":
    all_rows = []

    while True:
        try:
            # Wait for table
            WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "sample_1"))
            )
                
            # Get table rows
            rows = driver.find_elements(By.CSS_SELECTOR, "table#sample_1 tbody tr")
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if cols:
                    sr_no = cols[0].text.strip()

                    # Case Details (text + link)
                    case_link_element = cols[1].find_element(By.TAG_NAME, "a")
                    case_text = case_link_element.text.strip()
                    case_link_id = case_link_element.get_attribute("id")

                    party_details = cols[2].text.strip()
                    advocate_details = cols[3].text.strip()
                    reg_date = cols[4].text.strip()

                    all_rows.append({
                        "Sr.No": sr_no,
                        "Case ID": case_link_id,
                        "Case Details": case_text,
                        "Party Details": party_details,
                        "Advocate Details": advocate_details,
                        "Registration Date": reg_date
                    })

                # Check if "Next" is enabled
            next_btn = WebDriverWait(driver, 10).until(
               EC.element_to_be_clickable((By.CSS_SELECTOR, "#sample_1_next"))
)
            if "disabled" in next_btn.get_attribute("class"):
                break
            else:
                next_btn.click()
                time.sleep(2)

        except Exception as e:
            st.error(f"Error while fetching data: {e}")
            break

        # Show in Streamlit

    for row in all_rows:
        if st.button(f"{row['Case Details']} — {row['Party Details']}", key=row['Case ID']):
            try:

                st.session_state.selected_case = {
                "text": row['Case Details'],
                "link": row['Case ID'],
                "party": row['Party Details'],
                "advocate": row['Advocate Details'],
                "registration_date": row['Registration Date']
            }

                # Re-fetch the element just before clicking to avoid stale references
                fresh_case_element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, row['Case ID']))
                )
                driver.execute_script("arguments[0].click();", fresh_case_element)
                st.session_state.page = "Page3"
                st.success(f"Clicked on case: {row['Case Details']}")
                st.rerun()
            except Exception as e:
                st.error(f"Error clicking case '{row['Case Details']}': {e}")
elif st.session_state.page == "Page3":
    
    st.subheader(" Selected Case Details")

    case = st.session_state.selected_case

    df = pd.DataFrame([{
        "Case Title": case["text"],
        "Case Link": case["link"],
        "Party Details": case["party"],
        "Advocate Details": case["advocate"],
        "Registration Date": case["registration_date"] }])

    # Create a table with details
    st.table(df)

    # Button to trigger download (or other Selenium action)
    if st.button("Orders and Judgement"):
        try:

            order_and_judgement_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#loadmoreinfo button.btn.green"))  # change selector
            )
            st.session_state.page = "Page4"
            driver.execute_script("arguments[0].scrollIntoView(true);", order_and_judgement_button)

            driver.execute_script("arguments[0].click();", order_and_judgement_button)
            st.rerun()
        except Exception as e:
            st.error(f" Could not click download: {e}")

    # Back button
    if st.button("⬅ Back to Case List"):
        st.session_state.page = "Page2"
        driver.find_element(By.ID, "div_datatable~myfiltercasedetail").click()
        st.rerun()
elif st.session_state.page == "Page4":
       

    # Wait for 'Download All' button to be clickable
    download_all_btn = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.ID, "srchbackBtndiv1"))
    )

    # Click using JavaScript to avoid overlay/click interception issues
    driver.execute_script("arguments[0].click();", download_all_btn.find_element(By.CSS_SELECTOR, "button.btn.blue"))

    st.success("Download All button clicked!")
    
                    
                    

                                



                        

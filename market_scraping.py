
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import regex as re
import csv
import time
from pop_up_continue import WindowContinue
import json
from lxml import html
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

class ScrapingMarket():
    def __init__(self,main_driver,file_output_name):
        self.main_driver=main_driver
        self.file_output_name=file_output_name
        self.config=self.read_json('./variables.json')
        self.window_continue=WindowContinue()
        self.get_data()

        
    def read_json(self,variables_file):
        with open(variables_file, 'r') as file:
            config = json.load(file)            
        return config
    
    def clear_dict_list_variables(self):
        self.config['user_info']['user_level']=[]
        self.config['user_info']['user_trust_level']=[]
        self.config['market_info']['specialized']=[]
        self.config['user_info']['join_year_user']=[]
        self.config['user_info']['user_rating']= []
        self.config['market_info']['total_product']=[]
        self.config['sales_info']['total_sales']=[]
        self.config['quality_info']['total_reviews']=[]
        self.config['text']['all']=[]
        self.config['user_info']['user']=[]
        self.config['place_info']['place']=[]
        self.config['market_info']['price']=[]
        self.config['market_info']['payment_method']=[]
                
        
        self.config['user_info']['dict_user_level']={}
        self.config['user_info']['dict_trust_user_level']={}
        self.config['user_info']['dict_join_year_user']={}
        self.config['user_info']['dict_user_rating']={}
        self.config['market_info']['dict_total_product']={}
        self.config['sales_info']['dict_total_sales']={}
        self.config['quality_info']['dict_total_reviews']={}
            
    
    def continue_scrapping(self):
        result=self.window_continue.get_result()
        if result is None:
            print("Extraction finished.")
        else: 
            print(f"Scraping next category into “{result}”…")
            self.file_output_name=result
            self.get_data()
    
    def get_data(self):
        self.clear_dict_list_variables()
        matches=None
        matches_user=None
        lugar_match=None
        precio_match=None
        metodo_pago_match=None
        mercado=None
        user_level_match=None
        user_trust_level=None
        join_date_user=None
        user_rating=None
        total_sales=None
        reviews_user=None
        
        
        last_page=False
        page_number=2

        user_name_row=[]
        primera_vez=True
        while True:

            tree=html.fromstring(self.main_driver.page_source)
            old_text= self.main_driver.find_element(By.XPATH,".//td[1]/table/tbody/tr[1]/td/h6").text
            print("texto antiguo")
            print(old_text)
            path_expression='/html/body/div[2]/div/table/tbody/tr/td[2]/center/table/tbody/tr'
            rows=tree.xpath(path_expression)
            row_iteration=1
            column_iteration=1
            primer_scraping=True
            for row in rows:
                
                matches=row.xpath('.//td/table/tbody/tr[1]/td/h6//text()')
                matches=[t.strip() for t in matches if t.strip()]
                print(matches)

                
                matches_user=row.xpath('.//td/table/tbody/tr[2]/td[2]/h6/a/font/text()')
                matches_user=[re.match(r"^[^(]+",elem).group().strip() for elem in matches_user if re.match(r"^[^(]+",elem)]
                clean_matches_user=[item for item in matches_user if item != ')']
                
                lugar_match=row.xpath('.//td/table/tbody/tr[2]/td[2]/h6/text()')
                lugar_match=[t.strip() for t in lugar_match if t.strip()]
                print(lugar_match)
                if(len(lugar_match)<5):
                    lugar_filtrado=[lugar_match[1]]
                else:
                    lugar_filtrado=[lugar_match[1],lugar_match[4]]
                print(lugar_filtrado)
                
                precio_match=row.xpath('.//td/table/tbody/tr[2]/td[2]/h6/b/font/font/text()')
                precio_match=[t.strip() for t in precio_match if t.strip()]
                print(precio_match)
                
                metodo_pago_match=row.xpath('.//td/table/tbody/tr[2]/td[1]/center/button/text()')
                metodo_pago_match=[t.strip() for t in metodo_pago_match if t.strip()]
                print(metodo_pago_match)

                try:
                    self.main_driver.find_element(By.LINK_TEXT,"NEXT")
                except NoSuchElementException:
                    print("se esta procesando la ultima pagina o solo hay una")
                    last_page=True
                
                full_product_nam=[]
                
                print("usuarios")
                print(clean_matches_user)
                user_name_row=[]
                print(f"lista de usuarios guardados hasta ahora: {self.config['user_info']['user']}")
                print(len(clean_matches_user))
                for index,username in enumerate(clean_matches_user):
                    if matches[index] not in self.config['text']['all']:
                        print(f"procesando usuario: {username}")
                        if not any(username in sublist for sublist in self.config['user_info']['user']):
                            if username not in user_name_row: # si el usuario no esta en la lista de usuarios general pero si que coincide con el usuario de esa misma linea ,no se saca otra vez su level
                                
                                boton = self.main_driver.find_element(By.XPATH,f".//tr[{row_iteration}]/td[{column_iteration}]/table/tbody/tr[2]/td[2]/a")  #boton "ORDER"                  
                                self.main_driver.execute_script("arguments[0].scrollIntoView();",boton)
                                ActionChains(self.main_driver).key_down(Keys.CONTROL).click(boton).key_up(Keys.CONTROL).perform()
                                windows=self.main_driver.window_handles
                                self.main_driver.switch_to.window(windows[-1])
                                # WebDriverWait(driver,200).until(
                                #     lambda driver: driver.page_source != old_page_source and driver.current_url != old_url
                                # )
                                WebDriverWait(self.main_driver,200).until(
                                    EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/div/table/tbody/tr/td[2]/center/table/tbody/tr[1]/td[1]/table/tbody/tr[2]/td/table/tbody/tr/td[1]/button"))
                                                                            
                                )
                                print("pagina actualizada")
                                try:
                                    if primer_scraping:
                                        mercado=self.main_driver.find_element(By.XPATH,"/html/body/div[2]/div/table/tbody/tr/td[2]/center/table/tbody/tr[1]/td[2]/table/tbody/tr[2]/td/table/tbody/tr[3]/td[2]/h6/font").text
                                    #full_product_name=driver.find_element(By.XPATH,"/html/body/div[2]/div/table/tbody/tr/td[2]/b/center/font").text
                                    user_level_match=self.main_driver.find_element(By.XPATH,"/html/body/div[2]/div/table/tbody/tr/td[2]/center/table/tbody/tr[1]/td[1]/table/tbody/tr[2]/td/table/tbody/tr/td[1]/button").text
                                    user_trust_level=self.main_driver.find_element(By.XPATH,"/html/body/div[2]/div/table/tbody/tr/td[2]/center/table/tbody/tr[1]/td[1]/table/tbody/tr[2]/td/table/tbody/tr/td[2]/button").text
                                    #user_num_feedback=driver.find_element(By.XPATH,"/html/body/div[2]/div/table/tbody/tr/td[2]/center/div[1]/div/a[3]").text
                                    #shipping=driver.find_element(By.XPATH,"/html/body/div[2]/div/table/tbody/tr/td[2]/center/form/center/table/tbody/tr/td[2]/h6/font/font").text
                                    print(user_level_match)
                                    print(user_trust_level)
                                    #print(user_num_feedback)
                                    print(mercado)
                                    #print(shipping)
                                    user_level_match=re.search(r'\d+',user_level_match)
                                    if user_level_match:
                                        user_level_match=user_level_match.group()
                                        print("aqui")
                                    user_trust_level=re.search(r'\d+',user_trust_level)
                                    if user_trust_level:
                                        user_trust_level=user_trust_level.group()
                                    #user_num_feedback=re.search(r'\d+',user_num_feedback)
                                    # if user_num_feedback:
                                    #     user_num_feedback=user_num_feedback.group()
                                    print("AQUI")
                                except:
                                    self.main_driver.close()
                                    self.main_driver.switch_to.window(windows[0])
                                    break
                                time.sleep(2)
                                self.main_driver.close()
                                self.main_driver.switch_to.window(windows[0])
                                print("AQUI 2")
                                time.sleep(3)
                                if(not last_page):
                                    WebDriverWait(self.main_driver,200).until(
                                        EC.presence_of_element_located((By.LINK_TEXT,"NEXT"))
                                    )
                                self.config['user_info']['user_level'].append(user_level_match)
                                self.config['user_info']['user_trust_level'].append(user_trust_level)
                                user_name_row.append(username)
                                self.config['market_info']['specialized'].append(mercado)
                                print(user_name_row)
                                boton_user_profile = self.main_driver.find_element(By.XPATH,f".//tr[{row_iteration}]/td[{column_iteration}]/table/tbody/tr[2]/td[2]/h6/a")  
                                self.main_driver.execute_script("arguments[0].scrollIntoView();",boton_user_profile)
                                ActionChains(self.main_driver).key_down(Keys.CONTROL).click(boton_user_profile).key_up(Keys.CONTROL).perform()
                                windows=self.main_driver.window_handles
                                self.main_driver.switch_to.window(windows[-1])
                                WebDriverWait(self.main_driver,200).until(
                                    EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/div/table/tbody/tr[1]/td[2]/center/center/table[1]/tbody/tr/td[1]/table/tbody/tr[3]/td/table/tbody/tr[1]/td[1]/font"))
                                                                            
                                )
                                if column_iteration==2:
                                    row_iteration+=1
                                    column_iteration=1
                                else:
                                    column_iteration=2
                                try:
                                    join_date_user=self.main_driver.find_element(By.XPATH,"/html/body/div[2]/div/table/tbody/tr[1]/td[2]/center/center/table[1]/tbody/tr/td[1]/table/tbody/tr[3]/td/table/tbody/tr[2]/td[2]/h6").text
                                    user_rating=self.main_driver.find_element(By.XPATH,"/html/body/div[2]/div/table/tbody/tr[1]/td[2]/center/center/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td/table/tbody/tr[1]/td[2]/h6/b").text
                                    total_sales=self.main_driver.find_element(By.XPATH,"/html/body/div[2]/div/table/tbody/tr[1]/td[2]/center/center/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td/table/tbody/tr[2]/td/center/h6/font[1]/b/button").text
                                    reviews_user=self.main_driver.find_element(By.XPATH,"/html/body/div[2]/div/table/tbody/tr[1]/td[1]/center/table/tbody/tr[2]/td/h6/a").text
                                    print(f"Numero de reviews: {reviews_user}")
                                    print(total_sales)
                                    print(user_rating)
                                    reviews_user=re.search(r'\d+',reviews_user)
                                    if reviews_user:
                                        reviews_user=reviews_user.group()
                                    print(f"Numero de reviews(after parsing); {reviews_user}")
                                    user_rating=re.search(r'[\d.]+',user_rating)
                                    if user_rating:
                                        user_rating=user_rating.group()
                                    total_sales=total_sales.strip()
                                    print(total_sales)
                                    print(join_date_user)
                                    print(user_rating)
                                    tbody_struct=self.main_driver.find_elements(By.XPATH,"/html/body/div[2]/div/table/tbody/tr[1]/td[2]/center/center/table[2]/tbody/tr[2]/td/table/tbody/tr")
                                    print(tbody_struct)
                                    print("ha encontrado el elemnto")
                                    total_products=0
                                    for tr in tbody_struct:
                                        print("ENTRA 1")
                                        td_struct=tr.find_elements(By.XPATH,"./td")
                                        print(td_struct)
                                        print("encontrados")
                                        contador=0
                                        for td in td_struct:
                                            print(len(td_struct))
                                            print(f"ENTRADO : {contador}")
                                            contador=contador +1
                                            num_product_selling=td.text
                                            print(f"Numero productos:{num_product_selling}")
                                            num_product_selling=re.search(r'\d+',num_product_selling)
                                            print("sigue bien")
                                            if num_product_selling:
                                                print("no hay error")
                                                num_product_selling=num_product_selling.group()
                                                print(num_product_selling)
                                            total_products=total_products+int(num_product_selling)
                                            print(total_products)
                                    print(f"Products user: {total_products}")
                                except:
                                    self.main_driver.close()
                                    self.main_driver.switch_to.window(windows[0])
                                    print("FALLO EN CANTIDAD PRODUCTOS")
                                    break
                                time.sleep(2)
                                self.main_driver.close()
                                self.main_driver.switch_to.window(windows[0])
                                # WebDriverWait(driver,200).until(
                                #     EC.presence_of_element_located((By.LINK_TEXT,"Apply Filter"))
                                # )
                                self.config['user_info']['join_year_user'].append(join_date_user)
                                self.config['user_info']['user_rating'].append(user_rating)
                                self.config['sales_info']['total_sales'].append(total_sales)
                                self.config['quality_info']['total_reviews'].append(reviews_user)
                                self.config['market_info']['total_product'].append(total_products)
                                print(user_name_row)
                                if username not in self.config['user_info']['dict_user_level'].keys():
                                    if user_level_match is None:
                                        self.config['user_info']['dict_user_level'][username] = "None"
                                    else:
                                        self.config['user_info']['dict_user_level'][username] = user_level_match
                                    self.config['user_info']['dict_trust_user_level'][username]=user_trust_level
                                    #user_num_feedback_dict[username]=user_num_feedback
                                    self.config['user_info']['dict_user_rating'][username] = user_rating
                                    self.config['user_info']['dict_join_year_user'][username]=join_date_user
                                    print("---------------------------------")
                                    print(self.config['user_info']['dict_join_year_user'])
                                    print(f"Nuevo usuario añadido a dict: {username}")
                                    print("---------------------------------")
                                    self.config['market_info']['dict_total_product'][username]=total_products
                                    self.config['sales_info']['dict_total_sales'][username]=total_sales
                                    self.config['quality_info']['dict_total_reviews'][username]=reviews_user
                            else:
                                if column_iteration==2:
                                    row_iteration+=1
                                    column_iteration=1
                                else:
                                    column_iteration=2
                                self.config['user_info']['user_level'].append(self.config['user_info']['dict_user_level'].get(username))
                                self.config['user_info']['user_trust_level'].append(self.config['user_info']['dict_trust_user_level'].get(username))
                                self.config['market_info']['specialized'].append(mercado)
                                self.config['user_info']['join_year_user'].append(self.config['user_info']['dict_join_year_user'].get(username))
                                self.config['user_info']['user_rating'].append(self.config['user_info']['dict_user_rating'].get(username))
                                self.config['market_info']['total_product'].append(self.config['market_info']['dict_total_product'].get(username))
                                self.config['sales_info']['total_sales'].append(self.config['sales_info']['dict_total_sales'].get(username))
                                self.config['quality_info']['total_reviews'].append(self.config['quality_info']['dict_total_reviews'].get(username))
                                print(f"se ha añadido el mismo level que el de su row: {self.config['user_info']['dict_user_level'].get(username)}")
                        else:
                            if column_iteration==2:
                                row_iteration+=1
                                column_iteration=1
                            else:
                                column_iteration=2
                            self.config['user_info']['user_level'].append(self.config['user_info']['dict_user_level'].get(username))
                            self.config['user_info']['user_trust_level'].append(self.config['user_info']['dict_trust_user_level'].get(username))
                            self.config['market_info']['specialized'].append(mercado)
                            self.config['user_info']['join_year_user'].append(self.config['user_info']['dict_join_year_user'].get(username))
                            self.config['user_info']['user_rating'].append(self.config['user_info']['dict_user_rating'].get(username))
                            self.config['market_info']['total_product'].append(self.config['market_info']['dict_total_product'].get(username))
                            self.config['sales_info']['total_sales'].append(self.config['sales_info']['dict_total_sales'].get(username))
                            self.config['quality_info']['total_reviews'].append(self.config['quality_info']['dict_total_reviews'].get(username))
                            print(f"se ha añadido el mismo level que el de su row: {self.config['user_info']['dict_user_level'].get(username)}")
                            

                        print(row_iteration)
                        print(column_iteration)
                    else:
                        print(f"El producto {matches[index]} está duplicado") 
                        
                for index,product in enumerate(matches):
                    if product not in self.config['text']['all']:  
                        self.config['text']['all'].append(product)
                        self.config['user_info']['user'].append(clean_matches_user[index]) 
                        self.config['place_info']['place'].append(lugar_filtrado[index])
                        self.config['market_info']['price'].append(precio_match[index])
                        self.config['market_info']['payment_method'].append(metodo_pago_match[index])
                


            try:
            
                if(primera_vez):
                    primera_vez=False
                    try:
                        self.main_driver.find_element(By.LINK_TEXT,"NEXT")
                    except NoSuchElementException:
                        print("solo hay una")
                        break
                
                if(last_page):
                    print("HA ENTRADO EN EL BREAK")
                    break
                next_page= WebDriverWait(self.main_driver,200).until(
                    EC.presence_of_element_located((By.LINK_TEXT,"NEXT"))
                )
                next_page= WebDriverWait(self.main_driver,200).until(
                    EC.element_to_be_clickable((By.LINK_TEXT,"NEXT"))
                )
                print("Intentando hacer clik en NEXT...")
                next_page.click()
                print("Click en NEXT")
                time.sleep(5)
                WebDriverWait(self.main_driver,200).until(
                    lambda driver: driver.find_element(By.XPATH,".//td[1]/table/tbody/tr[1]/td/h6").text != old_text
                ) 
                print("ha cambiado TEXTOS")
                print(self.main_driver.find_element(By.XPATH,".//td[1]/table/tbody/tr[1]/td/h6").text)
                print("ha cambiado el contenido")
                time.sleep(5)
                print("Siguiente página cargada correctamente")
                
                try:
                    self.main_driver.find_element(By.LINK_TEXT,"NEXT")
                except NoSuchElementException:
                    print("se esta procesando la ultima pagina o solo hay una")
                    last_page=True
            
                    
                    
            except:
                print("No hay mas páginas disponibles")
                break


        df_data_extracted=pd.DataFrame({'Name Product': self.config['text']['all'], 'Seller': self.config['user_info']['user'],
                                      'Origin': self.config['place_info']['place'], 'Price': self.config['market_info']['price'],
                                      'Payment Method': self.config['market_info']['payment_method'],'User Level':self.config['user_info']['user_level'], 
                                      'User Trust Level': self.config['user_info']['user_trust_level'], "User Reviews": self.config['quality_info']['total_reviews'],"Specialized": self.config['market_info']['specialized'],
                                      "Join Date":self.config['user_info']['join_year_user'],"User Rating":self.config['user_info']['user_rating'],"User Products":self.config['market_info']['total_product'],
                                      "Total Sales" : self.config['sales_info']['total_sales']}).sort_values(by='Seller')
        df_data_extracted.to_csv(f"{self.file_output_name}.csv",index=False,sep=',')
        self.continue_scrapping()
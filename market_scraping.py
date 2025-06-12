
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import regex as re
import csv

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
    
    def continue_scrapping(self):
        result=self.window_continue.get_result()
        if result is None:
            print("Extraction finished.")
        else: 
            print(f"Scraping next category into “{result}”…")
            self.file_output_name=result
            self.get_data()
    
    def get_data(self):
        last_page=False
        page_number=2

        num_feedback_user=[]
        user_name_row=[]
        mercado_especializado=[]
        list_join_year_user=[]
        list_user_rating=[]
        list_total_sales=[]
        total_num_product=[]
        total_reviews_list=[]
        #forma_envio=[]
        users_levels={}
        trust_user_level={}
        user_num_feedback_dict={}
        joining_year_user={}
        total_sales_dict={}
        rate_user={}
        total_products_user={}
        total_reviews_dict={}
        primera_vez=True
        while True:

            tree=html.fromstring(driver.page_source)
            old_page_source=driver.page_source
            old_url=driver.current_url
            #print(old_url)
            #.//td/table/tbody/tr/td/h6/font/font/i
            # /html/body/div[2]/div/table/tbody/tr/td[2]/center/table/tbody/tr[1]/td[1]/table/tbody/tr[1]/td/h6/font/font/font/i
            # /html/body/div[2]/div/table/tbody/tr/td[2]/center/table/tbody/tr[2]/td[1]/table/tbody/tr[1]/td/h6/font/font/i
            old_text= driver.find_element(By.XPATH,".//td[1]/table/tbody/tr[1]/td/h6").text
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
                if(len(lugar_match)<5): #comprueba si la fila contiene uno o dos productos para que la extraccion sea la correcta
                    lugar_filtrado=[lugar_match[1]]
                else:
                    lugar_filtrado=[lugar_match[1],lugar_match[4]]
                #pattern_lugar=re.compile(r'^[\p{L}, ]+$') #\p{L}->captura todas las letras unicode, para paises con tildes o diactríticos
                #lugar_filtrado=[palabra for palabra in lugar_match if pattern_lugar.match(palabra)]  
                print(lugar_filtrado)
                
                precio_match=row.xpath('.//td/table/tbody/tr[2]/td[2]/h6/b/font/font/text()')
                precio_match=[t.strip() for t in precio_match if t.strip()]
                print(precio_match)
                
                metodo_pago_match=row.xpath('.//td/table/tbody/tr[2]/td[1]/center/button/text()')
                metodo_pago_match=[t.strip() for t in metodo_pago_match if t.strip()]
                print(metodo_pago_match)
                
                # productos_vendedor_match=row.xpath('.//td/table/tbody/tr[2]/td[1]/center/button/text()')
                # productos_vendedor_match=[t.strip() for t in metodo_pago_match if t.strip()]
                # print(productos_vendedor_match)
                
                try:
                    driver.find_element(By.LINK_TEXT,"NEXT")
                except NoSuchElementException:
                    print("se esta procesando la ultima pagina o solo hay una")
                    last_page=True
                
                full_product_nam=[]
                
                print("usuarios")
                print(clean_matches_user)
                user_name_row=[]
                print(f"lista de usuarios guardados hasta ahora: {user}")
                print(len(clean_matches_user))
                for index,username in enumerate(clean_matches_user):
                    if matches[index] not in self.config['text']['all']:
                        print(f"procesando usuario: {username}")
                        if not any(username in sublist for sublist in user):
                            if username not in user_name_row: # si el usuario no esta en la lista de usuarios general pero si que coincide con el usuario de esa misma linea ,no se saca otra vez su level
                                
                                boton = driver.find_element(By.XPATH,f".//tr[{row_iteration}]/td[{column_iteration}]/table/tbody/tr[2]/td[2]/a")  #boton "ORDER"                  
                                driver.execute_script("arguments[0].scrollIntoView();",boton)
                                ActionChains(driver).key_down(Keys.CONTROL).click(boton).key_up(Keys.CONTROL).perform()
                                windows=driver.window_handles
                                driver.switch_to.window(windows[-1])
                                # WebDriverWait(driver,200).until(
                                #     lambda driver: driver.page_source != old_page_source and driver.current_url != old_url
                                # )
                                WebDriverWait(driver,200).until(
                                    EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/div/table/tbody/tr/td[2]/center/table/tbody/tr[1]/td[1]/table/tbody/tr[2]/td/table/tbody/tr/td[1]/button"))
                                                                            
                                )
                                print("pagina actualizada")
                                try:
                                    if primer_scraping:
                                        mercado=driver.find_element(By.XPATH,"/html/body/div[2]/div/table/tbody/tr/td[2]/center/table/tbody/tr[1]/td[2]/table/tbody/tr[2]/td/table/tbody/tr[3]/td[2]/h6/font").text
                                    #full_product_name=driver.find_element(By.XPATH,"/html/body/div[2]/div/table/tbody/tr/td[2]/b/center/font").text
                                    user_level_match=driver.find_element(By.XPATH,"/html/body/div[2]/div/table/tbody/tr/td[2]/center/table/tbody/tr[1]/td[1]/table/tbody/tr[2]/td/table/tbody/tr/td[1]/button").text
                                    user_trust_level=driver.find_element(By.XPATH,"/html/body/div[2]/div/table/tbody/tr/td[2]/center/table/tbody/tr[1]/td[1]/table/tbody/tr[2]/td/table/tbody/tr/td[2]/button").text
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
                                    driver.close()
                                    driver.switch_to.window(windows[0])
                                    break
                                time.sleep(2)
                                driver.close()
                                driver.switch_to.window(windows[0])
                                print("AQUI 2")
                                time.sleep(3)
                                if(not last_page):
                                    WebDriverWait(driver,200).until(
                                        EC.presence_of_element_located((By.LINK_TEXT,"NEXT"))
                                    )
                                self.config['user_info']['user_level'].append(user_level_match)
                                self.config['user_info']['user_trust_level'].append(user_trust_level)
                                #num_feedback_user.append(user_num_feedback)
                                user_name_row.append(username)
                                mercado_especializado.append(mercado)
                                #full_product_nam.append(full_product_name)
                                #forma_envio.append(shipping)
                                print(user_name_row)
                                # if username not in users_levels.keys():
                                #     users_levels[username] = user_level_match
                                #     trust_user_level[username]=user_trust_level
                                #     user_num_feedback_dict[username]=user_num_feedback
                                boton_user_profile = driver.find_element(By.XPATH,f".//tr[{row_iteration}]/td[{column_iteration}]/table/tbody/tr[2]/td[2]/h6/a")  
                                driver.execute_script("arguments[0].scrollIntoView();",boton_user_profile)
                                ActionChains(driver).key_down(Keys.CONTROL).click(boton_user_profile).key_up(Keys.CONTROL).perform()
                                windows=driver.window_handles
                                driver.switch_to.window(windows[-1])
                                WebDriverWait(driver,200).until(
                                    EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/div/table/tbody/tr[1]/td[2]/center/center/table[1]/tbody/tr/td[1]/table/tbody/tr[3]/td/table/tbody/tr[1]/td[1]/font"))
                                                                            
                                )
                                if column_iteration==2:
                                    row_iteration+=1
                                    column_iteration=1
                                else:
                                    column_iteration=2
                                try:
                                    join_date_user=driver.find_element(By.XPATH,"/html/body/div[2]/div/table/tbody/tr[1]/td[2]/center/center/table[1]/tbody/tr/td[1]/table/tbody/tr[3]/td/table/tbody/tr[2]/td[2]/h6").text
                                    user_rating=driver.find_element(By.XPATH,"/html/body/div[2]/div/table/tbody/tr[1]/td[2]/center/center/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td/table/tbody/tr[1]/td[2]/h6/b").text
                                    total_sales=driver.find_element(By.XPATH,"/html/body/div[2]/div/table/tbody/tr[1]/td[2]/center/center/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td/table/tbody/tr[2]/td/center/h6/font[1]/b/button").text
                                    reviews_user=driver.find_element(By.XPATH,"/html/body/div[2]/div/table/tbody/tr[1]/td[1]/center/table/tbody/tr[2]/td/h6/a").text
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
                                    tbody_struct=driver.find_elements(By.XPATH,"/html/body/div[2]/div/table/tbody/tr[1]/td[2]/center/center/table[2]/tbody/tr[2]/td/table/tbody/tr")
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
                                    driver.close()
                                    driver.switch_to.window(windows[0])
                                    print("FALLO EN CANTIDAD PRODUCTOS")
                                    break
                                time.sleep(2)
                                driver.close()
                                driver.switch_to.window(windows[0])
                                # WebDriverWait(driver,200).until(
                                #     EC.presence_of_element_located((By.LINK_TEXT,"Apply Filter"))
                                # )
                                list_join_year_user.append(join_date_user)
                                list_user_rating.append(user_rating)
                                list_total_sales.append(total_sales)
                                total_reviews_list.append(reviews_user)
                                total_num_product.append(total_products)
                                print(user_name_row)
                                if username not in users_levels.keys():
                                    if user_level_match is None:
                                        users_levels[username] = "None"
                                    else:
                                        users_levels[username] = user_level_match
                                    trust_user_level[username]=user_trust_level
                                    #user_num_feedback_dict[username]=user_num_feedback
                                    rate_user[username] = user_rating
                                    joining_year_user[username]=join_date_user
                                    print("---------------------------------")
                                    print(joining_year_user)
                                    print(f"Nuevo usuario añadido a dict: {username}")
                                    print("---------------------------------")
                                    total_products_user[username]=total_products
                                    total_sales_dict[username]=total_sales
                                    total_reviews_dict[username]=reviews_user
                            else:
                                if column_iteration==2:
                                    row_iteration+=1
                                    column_iteration=1
                                else:
                                    column_iteration=2
                                self.config['user_info']['user_level'].append(users_levels.get(username))
                                self.config['user_info']['user_trust_level'].append(trust_user_level.get(username))
                                num_feedback_user.append(user_num_feedback_dict.get(username))
                                mercado_especializado.append(mercado)
                                list_join_year_user.append(joining_year_user.get(username))
                                list_user_rating.append(rate_user.get(username))
                                total_num_product.append(total_products_user.get(username))
                                list_total_sales.append(total_sales_dict.get(username))
                                total_reviews_list.append(total_reviews_dict.get(username))
                                print(f"se ha añadido el mismo level que el de su row: {users_levels.get(username)}")
                        else:
                            if column_iteration==2:
                                row_iteration+=1
                                column_iteration=1
                            else:
                                column_iteration=2
                            self.config['user_info']['user_level'].append(users_levels.get(username))
                            self.config['user_info']['user_trust_level'].append(trust_user_level.get(username))
                            num_feedback_user.append(user_num_feedback_dict.get(username))
                            mercado_especializado.append(mercado)
                            list_join_year_user.append(joining_year_user.get(username))
                            list_user_rating.append(rate_user.get(username))
                            total_num_product.append(total_products_user.get(username))
                            list_total_sales.append(total_sales_dict.get(username))
                            total_reviews_list.append(total_reviews_dict.get(username))
                            print(f"se ha añadido el mismo level que el de su row: {users_levels.get(username)}")
                            
                            # pattern_userlevel=re.compile(r'^[0-9]+$')
                            # lugar_filtrado=[if pattern_userlevel.match(user_level_match):]
                        print(row_iteration)
                        print(column_iteration)
                    else:
                        print(f"El producto {matches[index]} está duplicado") 
                        
                for index,product in enumerate(matches):
                    if product not in self.config['text']['all']:  
                        #print(len(full_product_nam))
                        self.config['text']['all'].append(product)
                # for index,usernam in enumerate(clean_matches_user):
                #     if user not in user: 
                        self.config['user_info']['user'].append(clean_matches_user[index])
                # for index,origin in enumerate(lugar_filtrado):
                #     if origin not in lugar: 
                        self.config['place_info']['place'].append(lugar_filtrado[index])
                # for index,prices in enumerate(precio_match):
                #     if prices not in precio: 
                        self.config['market_info']['price'].append(precio_match[index])
                # for index,payment in enumerate(metodo_pago):
                #     if payment not in textos: 
                        self.config['market_info']['payment_method'].append(metodo_pago_match[index])
                
            print(textos)
            print(user)
            print(lugar)
            print(precio)
            print(metodo_pago)
            print(user_level)
            print(trust_level)
            #print(num_feedback_user)
            print(list_join_year_user)
            print(total_num_product)
            print(list_user_rating)
            print(list_total_sales)


            try:
                #driver.execute_script("arguments[0].scrollIntoView();",driver.find_element(By.LINK_TEXT,"NEXT"))
                if(primera_vez):
                    primera_vez=False
                    try:
                        driver.find_element(By.LINK_TEXT,"NEXT")
                    except NoSuchElementException:
                        print("solo hay una")
                        break
                
                if(last_page):
                    print("HA ENTRADO EN EL BREAK")
                    break
                next_page= WebDriverWait(driver,200).until(
                    EC.presence_of_element_located((By.LINK_TEXT,"NEXT"))
                )
                next_page= WebDriverWait(driver,200).until(
                    EC.element_to_be_clickable((By.LINK_TEXT,"NEXT"))
                )
                print("Intentando hacer clik en NEXT...")
                next_page.click()
                print("Click en NEXT")
                time.sleep(5)
                WebDriverWait(driver,200).until(
                    #lambda driver: driver.execute_script("return document.readyState")== "complete"
                    lambda driver: driver.find_element(By.XPATH,".//td[1]/table/tbody/tr[1]/td/h6").text != old_text
                ) 
                print("ha cambiado TEXTOS")
                print(driver.find_element(By.XPATH,".//td[1]/table/tbody/tr[1]/td/h6").text)
                print("ha cambiado el contenido")
                time.sleep(5)
                print("Siguiente página cargada correctamente")
                
                try:
                    driver.find_element(By.LINK_TEXT,"NEXT")
                except NoSuchElementException:
                    print("se esta procesando la ultima pagina o solo hay una")
                    last_page=True
            
                    
                    
            except:
                print("No hay mas páginas disponibles")
                break


        df_product_name=pd.DataFrame({'Name Product': self.config['text']['all'], 'Seller': self.config['user_info']['user'],
                                      'Origin': self.config['place_info']['place'], 'Price': self.config['market_info']['price'],
                                      'Payment Method': self.config['market_info']['payment_method'],'User Level':self.config['user_info']['user_level'], 
                                      'User Trust Level': user_trust_level, "User Reviews": total_reviews_list,"Specialized": mercado_especializado,
                                      "Join Date":list_join_year_user,"User Rating":list_user_rating,"User Products":total_num_product,
                                      "Total Sales" : list_total_sales}).sort_values(by='Seller')
        df_product_name.to_csv("torzo_thc_others.csv",index=False,sep=',')
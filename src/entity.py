from pydantic import BaseModel

class Company(BaseModel):
    id : str
    shared_values: str
    city: str
    product: str




my_list = [{"id":"1","shared_values":"Teamwork","city":"Utrecht","product":"axual-platform"},
           {"id":"2","shared_values":"Innovation","city":"Amsterdam","product":"green-energy-solution"},
           {"id":"3","shared_values":"Innovation","city":"Amsterdam","product":"tech-gadgets"},
           {"id":"4","shared_values":"Diversity","city":"Amsterdam","product":"software-solution"}
           ]



for i in my_list:
  #  print(i["id"],i["shared_values"],i["city"],i["product"])
    company = Company(id=i["id"],shared_values=i["shared_values"],city=i["city"],product=i["product"])
    print(company.json())


#sfor i in range(2):

 #   print(my_list[i]["id"],my_list[i]["shared_values"],my_list[i]["city"],my_list[i]["product"])
   
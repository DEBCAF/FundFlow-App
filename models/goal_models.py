class Goal():
    def __init__(self, name, description, amount, date_created, due_date, status):
        self.name = name
        self.description = description
        self.amount = amount
        self.date_created = date_created
        self.due_date = due_date
        self.status = status

    def __str__(self):
        return self.name
    
    def check_if_reached(self):
        if self.status == "completed":
            return True
        else:
            return False
        
    def set_status(self, status):
        self.status = status
        
    def get_status(self):
        return self.status
    
    def get_name(self):
        return self.name
    
    def get_description(self):
        return self.description
    
    def get_amount(self):
        return self.amount
    
    def get_date_created(self):
        return self.date_created
    
    def get_due_date(self):
        return self.due_date
    
    def set_name(self, name):
        self.name = name
        
    def set_description(self, description):
        self.description = description
        
    def set_amount(self, amount):
        self.amount = amount
        

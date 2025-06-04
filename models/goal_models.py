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
    
    
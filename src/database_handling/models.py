class Category:
    
    def to_dict(self):
        return {
            'name': self.name,
            'email': self.email,
            'age': self.age
        }
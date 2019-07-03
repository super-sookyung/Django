"""
TODO list for Account App

1. Set User Model full_clean method
- Disallow passwords with only numbers or characters
- Set a certain password logic! 
- Then check if full_clean is checked by serializer.is_valid() method, 
if not put it in the View logic! 
- Don't override .save() method unless we really need to. It will not be called
when doing bulk creation

2. Set User Tokens! 

3. Create a away to check if slug_username or email is taken already!
- Since qs.exists() is a good way to check whether a field is not unique or not,
it has its bad parts. 
Django does not lock its database when doing committing to the database!
This in fact creates a race_condition. And can create a 

4. Set throttling for Certain UserViews. 

5. Maybe change our Hashing Algorithms?

6. Transaction Atomic on User Slug creation. Retry if
	Integreity Error

"""

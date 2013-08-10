import webapp2
form="""
	<form method="post">
		<label>Please enter some text here</label><br>
		<textarea name="text">{value}</textarea><br>
		<input type="submit">
	</form>
	"""

class MainPage(webapp2.RequestHandler):
    def get(self):
        #self.response.headers['Content-Type'] = 'text/plan"
        self.response.write(form)
    def post(self):
        #self.response.headers['Content-Type'] = 'text/plain"
        p = self.request.get("text")
        p = convert(p)
        self.response.write(form.format(value=p))
    
def convert(value):
    output_str= "";
    for i in value:
    	if (i >= 'a' and i <= 'z') or (i >= 'A' and i <= 'Z'):
    		output_chr = ord(i) + 13
    		if (output_chr > ord('z')):
  			output_chr -= 26 	
    		elif (i > 'M' and i <= 'Z'):
    			print output_chr
    			output_chr -= 26
    			
 		i = chr(output_chr)
    	output_str += i
    return escape_html(output_str)

def escape_html(s):
    for (i,o) in (('&','&amp;'),('>','&gt;'),('<','&lt;'),('"','&quot;')):
        s=s.replace(i,o)
    return s

application = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)


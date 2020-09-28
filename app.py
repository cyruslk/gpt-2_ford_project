import copy
import tornado.ioloop
import tornado.locks
import tornado.web
import tornado.websocket
import os.path
from tornado.options import define, options,parse_command_line
import tornado.gen as gen
import gpt_2_simple as gpt2
import requests

define("port", default=8880, help="run the server on the given port")
define("debug", default=True, help="run in debug mode")
define("threshold", default=7, help="length of words before model generates text")
define("text_length", default=100, help="length of words generated")


class ModelHandler(object):

	def __init__(self):
		self.cache = ""
		self.threshold = options.threshold # default
		self.generated_text = ""
		self.results = ""
		self.sess = None
		self.initializeModel()

	def initializeModel(self):
	
		self.sess = gpt2.start_tf_sess()
		gpt2.load_gpt2(self.sess)


	async def generate_text(self, prefix, text_length=options.text_length):
		gen_text = gpt2.generate(self.sess, 
		length=text_length,
		prefix=prefix,
		temperature=0.5, 
		return_as_list=True)[0]

		text = gen_text.replace('\n', ' ')
		sentences = text.split('.')
		clean_text = '. '.join(sentences[:-1])+"."

		self.results=clean_text;

	async def add_message(self, prefix):
		self.cache+=prefix
		if(len(self.cache)>self.threshold):
			await self.generate_text(self.cache)



model_handler = ModelHandler()
model_handler.threshold = options.threshold


class Generator(tornado.websocket.WebSocketHandler):

	def check_origin(self, origin):
		return True
	def open(self):
		self.model_handler_gen = copy.copy(model_handler)
	async def on_message(self, message):
		await self.model_handler_gen.add_message(message)

		self.write_message(self.model_handler_gen.results)


def main():
	parse_command_line()
	app = tornado.web.Application([
			(r"/generator", Generator),
	])
	app.listen(options.port)
	tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
	main()
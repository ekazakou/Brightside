"""
File             : sender.py
Author           : ian
Created          : 08-04-2017

Last Modified By : ian
Last Modified On : 08-05-2017
***********************************************************************
The MIT License (MIT)
Copyright © 2017 Ian Cooper <ian_hammond_cooper@yahoo.co.uk>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the “Software”), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
***********************************************************************
"""

import logging
import time

from multiprocessing import Queue

from arame.gateway import ArameConsumer
from brightside.connection import Connection
from brightside.command_processor import CommandProcessor, Request
from brightside.dispatch import ConsumerConfiguration, Dispatcher
from brightside.messaging import BrightsideConsumerConfiguration, BrightsideMessage
from brightside.registry import Registry
from arame.messaging import JsonRequestSerializer
from src.core import HelloWorldCommand, HelloWorldCommandHandler


def command_processor_factory(channel_name:str):
    handler = HelloWorldCommandHandler()

    subscriber_registry = Registry()
    subscriber_registry.register(HelloWorldCommand, lambda: handler)

    command_processor = CommandProcessor(
        registry=subscriber_registry
    )
    return command_processor


def consumer_factory(connection: Connection, consumer_configuration: BrightsideConsumerConfiguration, logger: logging.Logger):
    return ArameConsumer(connection=connection, configuration=consumer_configuration, logger=logger)


def map_my_command_to_request(message: BrightsideMessage) -> Request:
    return JsonRequestSerializer(request=HelloWorldCommand(), serialized_request=message.body.value)\
        .deserialize_from_json()


def run():
    pipeline = Queue()
    connection = Connection("amqp://guest:guest@localhost:5762/%2f", "examples.perfomer.exchange")
    configuration = BrightsideConsumerConfiguration(pipeline, "examples.greetings.queue", "hello_world")
    consumer = ConsumerConfiguration(connection, configuration, consumer_factory, command_processor_factory, map_my_command_to_request)
    dispatcher = Dispatcher({"MyCommand": consumer})

    dispatcher.receive()

    time.sleep(10)

    dispatcher.end()


if __name__ == "__main__":
    run()
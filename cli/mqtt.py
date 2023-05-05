import click
import logging as log

import cli.util

from libflagship.mqttapi import AnkerMQTTBaseClient

servertable = {
    "eu": "make-mqtt-eu.ankermake.com",
    "us": "make-mqtt.ankermake.com",
}


def mqtt_open(env):
    with env.config.open() as cfg:
        if env.printer >= len(cfg.printers):
            log.fatal(f"Printer number {env.printer} out of range, max printer number is {len(cfg.printers)-1} ")
            return
        printer = cfg.printers[env.printer]
        acct = cfg.account
        server = servertable[acct.region]
        env.log.info(f"Connecting printer {printer.p2p_duid} through {server}")
        client = AnkerMQTTBaseClient.login(
            printer.sn,
            acct.mqtt_username,
            acct.mqtt_password,
            printer.mqtt_key,
            ca_certs="examples/ankermake-mqtt.crt",
            verify=not env.insecure,
        )
        client.connect(server)
        return client


def mqtt_command(client, msg):
    client.command(msg)

    reply = client.await_response(msg["commandType"])
    if reply:
        click.echo(cli.util.pretty_json(reply))
    else:
        log.error("No response from printer")

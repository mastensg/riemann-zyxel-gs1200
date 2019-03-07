#!/usr/bin/env python3

import configparser
import pathlib
import pprint
import sys
import time

import bernhard
import pyjsparser
import requests
import schedule

# riemann metric fields:
"""
# per instance of this program
time            The time of the event, in unix epoch seconds
ttl             A floating-point time, in seconds, that this event is considered valid for.
tags            Freeform list of strings, e.g. ["rate", "fooproduct", "transient"]

# per switch
host            A hostname, e.g. "api1", "foo.com"

# per metric
service         e.g. "API port 8000 reqs/sec"
metric          A number associated with this event, e.g. the number of reqs/sec.
state           Any string less than 255 bytes, e.g. "ok", "warning", "critical"
description     Freeform text
"""

##############################################################################


def decl_of_doc(doc, index, name):
    var = doc["body"][index]
    assert "var" == var["kind"]
    assert "VariableDeclaration" == var["type"]

    decl = var["declarations"][0]
    assert "Identifier" == decl["id"]["type"]
    assert name == decl["id"]["name"]

    return decl


def literal_of_doc(doc, index, name, classinfo):
    decl = decl_of_doc(doc, index, name)
    assert "Literal" == decl["init"]["type"]

    value = decl["init"]["value"]
    assert isinstance(value, classinfo)

    return value


def literal_of_array(array, index, classinfo):
    element = array["elements"][index]
    assert "Literal" == element["type"]

    value = element["value"]
    assert isinstance(value, classinfo)

    return value


##############################################################################

# igmp_data.js  ##############################################################

# TODO(mastensg)

# LAG_data.js  ###############################################################

# TODO(mastensg)

# link_data.js  ##############################################################


def metrics_of_link(doc):
    def port_link_up():
        decl = decl_of_doc(doc, 0, "portstatus")

        elements = decl["init"]["elements"]
        assert 5 == len(elements)
        for i in range(5):
            element = elements[i]

            assert "Literal" == element["type"]

            value = element["value"]
            assert isinstance(value, str)
            assert value in ("Down", "Up")

            port_number = i + 1

            yield {
                "service": "port {} link up".format(port_number),
                "metric": 1.0 if "Up" == value else 0.0,
                "state": value.lower(),
            }

    def port_speed():
        decl = decl_of_doc(doc, 1, "speed")

        elements = decl["init"]["elements"]
        assert 5 == len(elements)
        for i in range(5):
            element = elements[i]

            assert "Literal" == element["type"]

            value = element["value"]
            assert isinstance(value, str)

            number_str, unit = value.split()
            assert "Mbps" == unit
            number_int = int(number_str)
            number = float(number_int)

            port_number = i + 1

            yield {
                "service": "port {} link speed".format(port_number),
                "metric": number,
            }

    def port_stats():
        decl = decl_of_doc(doc, 2, "Stats")

        rows = decl["init"]["elements"]
        assert 5 == len(rows)
        for i in range(5):
            row = rows[i]

            assert "ArrayExpression" == row["type"]
            assert 11 == len(row["elements"])

            tx = sum(literal_of_array(row, i, float) for i in (1, 2, 3))
            rx = sum(literal_of_array(row, i, float) for i in (6, 7, 8))

            port_number = i + 1

            yield {
                "service": "port {} tx packets".format(port_number),
                "metric": tx,
            }

            yield {
                "service": "port {} rx packets".format(port_number),
                "metric": rx,
            }

    yield from port_link_up()
    yield from port_speed()
    yield from port_stats()


# loop_data.js  ##############################################################

# TODO(mastensg)

# mirror_data.js  ############################################################

# TODO(mastensg)

# poe_data.js  ###############################################################


def metrics_of_poe(doc):
    def port_power():
        decl = decl_of_doc(doc, 2, "port_power")

        elements = decl["init"]["elements"]
        assert 4 == len(elements)
        for i in range(4):
            element = elements[i]

            assert "Literal" == element["type"]

            value = element["value"]
            assert isinstance(value, float)

            port_number = i + 1

            yield {
                "service": "port {} power".format(port_number),
                "metric": value,
            }

    yield {
        "service": "total power",
        "metric": literal_of_doc(doc, 0, "total_power", float),
    }

    yield {
        "service": "max led power",
        "metric": literal_of_doc(doc, 1, "max_led_power", float),
    }

    yield from port_power()

    yield {
        "service": "total real power",
        "metric": literal_of_doc(doc, 3, "total_real_power", float),
    }


# port_state_data.js  ########################################################

# TODO(mastensg)

# qos_data.js  ###############################################################

# TODO(mastensg)

# rate_data.js  ##############################################################

# TODO(mastensg)

# system_data.js  ############################################################


def metrics_of_system(doc):
    description = ("""ports:          {}
model name:     {}
device name:    {}
build date:     {}
mac:            {}
ip:             {}
subnet mask:    {}
gateway:        {}
dhcp state:     {}""".format(
        int(literal_of_doc(doc, 0, "Max_port", str)),
        literal_of_doc(doc, 1, "model_name", str),
        literal_of_doc(doc, 2, "sys_dev_name", str),
        literal_of_doc(doc, 4, "sys_bld_date", str),
        literal_of_doc(doc, 5, "sys_MAC", str),
        literal_of_doc(doc, 6, "sys_IP", str),
        literal_of_doc(doc, 7, "sys_sbnt_msk", str),
        literal_of_doc(doc, 8, "sys_gateway", str),
        literal_of_doc(doc, 9, "sys_dhcp_state", str),
    ))
    # 10 sys_first_login
    # 11 loop
    # 12 loop_status
    # 13 logined
    # 14 isTrunk
    # 15 sys_eee_state

    yield {
        "service": "system",
        "state": "ok",
        "description": description,
    }


# VLAN_1Q_List_data.js  ######################################################

# TODO(mastensg)

##############################################################################


def test_main():
    def parse_example(prefix):
        def fmt(value):
            return pprint.pformat(value, width=120) + "\n"

        def output(out_dir, prefix, contents):
            pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
            path = "{}/{}.txt".format(out_dir, prefix)
            with open(path, "w") as f:
                f.write(contents)

        js_path = "examples/{}_data.js".format(prefix)
        js = open(js_path).read()

        doc = pyjsparser.PyJsParser().parse(js)

        output("examples_doc", prefix, fmt(doc))

        metrics_of = globals()["metrics_of_{}".format(prefix)]
        metrics = list(metrics_of(doc))

        output("examples_metrics", prefix, fmt(metrics))

        return

    parse_example("link")
    parse_example("poe")
    parse_example("system")

    return


##############################################################################


def metrics_of_host(host):
    address = host["address"]
    hostname = host["hostname"]

    def log_in():
        data = {"password": host["password"]}
        r = requests.post("http://{}/login.cgi".format(address), data=data)
        assert 200 == r.status_code
        if "Incorrect password, please try again." in r.text:
            raise ValueError("Wrong password for switch at {}".format(address))

    log_in()

    for prefix in ("link", "poe", "system"):
        r = requests.get("http://{}/{}_data.js".format(address, prefix))
        assert 200 == r.status_code
        assert not r.text.startswith("<")

        doc = pyjsparser.PyJsParser().parse(r.text)
        metrics_of = globals()["metrics_of_{}".format(prefix)]

        for m in metrics_of(doc):
            m["host"] = hostname
            yield m


def hosts_of_config(config):
    for s in config.sections():
        assert "address" in config[s]
        assert "password" in config[s]
        yield {
            "hostname": s,
            "address": config[s]["address"],
            "password": config[s]["password"],
        }


def report_main():
    defaults = {
        "riemann_host": "localhost",
        "riemann_port": "5555",
        "interval": "60",
        "ttl": "120",
        "tag": "zyxel-gs1200",
    }
    config = configparser.ConfigParser(defaults=defaults)
    config.read(sys.argv[1:])

    hosts = list(hosts_of_config(config))
    interval = int(config["DEFAULT"]["interval"])
    riemann_host = config["DEFAULT"]["riemann_host"]
    riemann_port = int(config["DEFAULT"]["riemann_port"])
    tag = config["DEFAULT"]["tag"]
    ttl = int(config["DEFAULT"]["ttl"])

    riemann_client = bernhard.Client(host=riemann_host, port=riemann_port)

    def it():
        for h in hosts:
            for m in metrics_of_host(h):
                m["ttl"] = ttl
                m["tags"] = [tag]
                if not "state" in m:
                    m["state"] = "ok"

                riemann_client.send(m)

    # TODO(mastensg): stop drift: https://github.com/blakev/gevent-tasks
    schedule.every(interval).seconds.do(it)
    schedule.run_all()

    while True:
        schedule.run_pending()
        time.sleep(schedule.idle_seconds())


##############################################################################


def main():
    report_main()


if __name__ == "__main__":
    main()

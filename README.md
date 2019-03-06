This program collects metrics from the web interface of [Zyxel GS1200][1] PoE switches, and submits them to [Riemann][2].
Collected metrics include
- power usage per port,
- number of packets received and transmitted per port,
- link status and speed per port,
- total power usage, and
- system information such as firmware version and mac address.

A [riemann-dash][3] dashboard fed by this program may look like this:

![Screenshot of riemann-dash](dash.png)

## How to run

```
pip3 install --user riemann-zyxel-gs1200
cp example.ini my_configuration.ini
edit my_configuration.ini
python3 -m riemann_zyxel_gs1200 my_configuration.ini
```

## License

Copyright (c) 2019, Martin Stensgård.
All rights reserved.

riemann-zyxel-gs1200 is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, only version 3 of the License.

riemann-zyxel-gs1200 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with riemann-zyxel-gs1200. If not, see <http://www.gnu.org/licenses/>.

[1]: https://www.zyxel.com/products_services/5-Port-8-Port-Web-Managed-PoE-Gigabit-Switch-GS1200-5HP-v2-GS1200-8HP-v2/
[2]: http://riemann.io/
[3]: https://github.com/riemann/riemann-dash
[dash.png]: https://cdn.jsdelivr.net/gh/mastensg/riemann-zyxel-gs1200/dash.png

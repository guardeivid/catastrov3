# CatastroV3

Plugin para QGIS 3.

```txt
    begin       : 2019-02-18
    copyright   : (C) 2019 by David Orellano
    authors     : David Orellano
    email       : guardeivid@yahoo.com.ar
```

Plugin CatastroV3 QGIS permite realizar búsquedas catastrales, por partida inmobiliaria o nomenclatura catastral de la Provincia de Buenos Aires.

A través de método local (configurando parámetros de conexión a base de datos PostGis propia) o a servicios de mapas web de la Agencia de Recaudación de la Provincia de Buenos Aires (ARBA).


## Instalación

### Clonando el repositorio desde Github:

```sh
git clone https://github.com/guardeivid/catastrov3.git
cp catastrov3 ~/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins
cd ~/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins
mv catastrov3 CatastroV3
```

### o desde la aplicación QGIS:

1. Menú Complementos -> Administrar e instalar complementos...
2. Menú Complementos Configuración -> Seleccionar Mostrar también los complementos experimentales
3. Selecciona el plugin CatastroV3 de la lista de Complementos No Instalados
4. Instalar el plugin


## Documentación

### Configuración

```txt
Seleccionar modo (local | web)
```

#### Modo Local
```txt
Configurar parámetros de conexión:

HostName: 'localhost'
Port: 5432
DatabaseName: ''
UserName: ''
Password: ''
```

```txt
Configurar nombres de tablas:

Schema: 'public'
Departamento: 'departamento'
Circunscripcion: 'circunscripcion'
Sección: 'seccion'
Chacra: 'chacra'
Quinta: 'quinta'
Fracción: 'fraccion'
Manzana: 'manzana'
Parcela: 'parcela'
```

### Búsquedas

#### Por Partida Inmobiliaria

Seleccionar partido e introducir el número de partida.

#### Por Nomenclatura Catastral

Seleccionar partido e introducir los datos de nomenclatura.
Hay búsquedas parciales según que campos se hallan completados.


### Resultados

> Las capas con los resultados de las búsquedas son temporales, es decir que cuando se cierre el programa se perderán.

Los resultados por defecto se agregan en capas con estilo por defecto.

Se pueden agregar en nuevas capas.

Se puede usar un estilo aleatorio al agregar una nueva capa de resultados.


## Licencia
Version: MPL 2.0/GPL 2.0/LGPL 2.1

The contents of this file are subject to the Mozilla Public License Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.mozilla.org/MPL/

Alternatively, the contents of this file may be used under the terms of either of the GNU General Public License Version 2 or later (the "GPL"), or the GNU Lesser General Public License Version 2.1 or later (the "LGPL"), in which case the provisions of the GPL or the LGPL are applicable instead of those above. If you wish to allow use of your version of this file only under the terms of either the GPL or the LGPL, and not to allow others to use your version of this file under the terms of the MPL, indicate your decision by deleting the provisions above and replace them with the notice and other provisions required by the GPL or the LGPL. If you do not delete the provisions above, a recipient may use your version of this file under the terms of any one of the MPL, the GPL or the LGPL.

Software distributed under the License is distributed on an "AS IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the specific language governing rights and limitations under the License.

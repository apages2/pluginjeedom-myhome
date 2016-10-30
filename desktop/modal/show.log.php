<?php
/* This file is part of Jeedom.
 *
 * Jeedom is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Jeedom is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Jeedom. If not, see <http://www.gnu.org/licenses/>.
 */


if (!isConnect('admin')) {
    throw new Exception('401 Unauthorized');
}
sendVarToJs('debugMode_slaveId', init('slave_id'));
?>
<div class="alert alert-warning">{{Pensez bien à activer l'écriture de tous les messages dans la configuration du plugin et à redémarrer le démon une fois cela fait (N'oubliez pas de tout désactiver une fois fini)}}</div>
<a class="btn btn-warning pull-right" data-state="1" id="bt_myhomeLogStopStart"><i class="fa fa-pause"></i> {{Pause}}</a>
<input class="form-control pull-right" id="in_myhomeLogSearch" style="width : 300px;" placeholder="{{Rechercher}}" />
<br/><br/><br/>
<pre id='pre_rfxlog' style='overflow: auto; height: 80%;with:90%;'></pre>


<script>
   jeedom.log.autoupdate({
    log : 'myhome.message',
    slaveId : debugMode_slaveId,
    display : $('#pre_myhomelog'),
    search : $('#in_myhomeLogSearch'),
    control : $('#bt_myhomeLogStopStart'),
});
</script>
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
$eqLogics = myhome::byType('myhome');
?>

<table class="table table-condensed tablesorter" id="table_healthmyhome">
	<thead>
		<tr>
			<th>{{Image}}</th>
			<th>{{Module}}</th>
			<th>{{ID}}</th>
			<th>{{Statut}}</th>
			<th>{{Signal}}</th>
			<th>{{Dernière communication}}</th>
			<th>{{Date création}}</th>
		</tr>
	</thead>
	<tbody>
	 <?php
foreach ($eqLogics as $eqLogic) {
	$device_id = substr($eqLogic->getConfiguration('device'), 0, strpos($eqLogic->getConfiguration('device'), ':'));
	$id_full = str_replace('::', '_', $eqLogic->getConfiguration('device'));
	$alternateImg = $eqLogic->getConfiguration('iconModel');
	if (file_exists(dirname(__FILE__) . '/../../core/config/devices/' . $alternateImg . '.jpg')) {
		$img = '<img class="lazy" src="plugins/myhome/core/config/devices/' . $alternateImg . '.jpg" height="65" width="55" />';
	} elseif (file_exists(dirname(__FILE__) . '/../../core/config/devices/' . $eqLogic->getConfiguration('device') . '.jpg')) {
		$img = '<img class="lazy" src="plugins/myhome/core/config/devices/' . $eqLogic->getConfiguration('device') . '.jpg" height="65" width="55" />';
	} else {
		$img = '<img class="lazy" src="plugins/myhome/doc/images/myhome_icon.png" height="65" width="55" />';
	}
	$signalcmd = $eqLogic->getCmd('info', 'signal');
	$signal = '';
	if (is_object($signalcmd)) {
		$signal = $signalcmd->execCmd();
	}
	echo '<tr><td>' . $img . '</td><td><a href="' . $eqLogic->getLinkToConfiguration() . '" style="text-decoration: none;">' . $eqLogic->getHumanName(true) . '</a></td>';
	echo '<td><span class="label label-info" style="font-size : 1em;">' . $eqLogic->getId() . '</span></td>';
	$status = '<span class="label label-success" style="font-size : 1em;">{{OK}}</span>';
	if ($eqLogic->getStatus('state') == 'nok') {
		$status = '<span class="label label-danger" style="font-size : 1em;">{{NOK}}</span>';
	}
	echo '<td>' . $status . '</td>';
	$signalLevel = 'success';
	if ($signal <= 2) {
		$signalLevel = 'danger';
	} elseif ($signal <= 5) {
		$signalLevel = 'warning';
	}
	echo '<td><span class="label label-' . $signalLevel . '" style="font-size : 1em;">' . $signal . '</span></td>';
	echo '<td><span class="label label-info" style="font-size : 1em;">' . $eqLogic->getStatus('lastCommunication') . '</span></td>';
	echo '<td><span class="label label-info" style="font-size : 1em;">' . $eqLogic->getConfiguration('createtime') . '</span></td>';
	echo '</tr>';
}
?>
	</tbody>
</table>

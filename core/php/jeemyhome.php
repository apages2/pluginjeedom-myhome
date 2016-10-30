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
require_once dirname(__FILE__) . "/../../../../core/php/core.inc.php";

if (!jeedom::apiAccess(init('apikey'))) {
	connection::failed();
	echo 'Clef API non valide, vous n\'êtes pas autorisé à effectuer cette action (jeemyhome)';
	die();
}

if (isset($_GET['test'])) {
	echo 'OK';
	die();
}

if (isset($_GET['trame'])) {


	$trame = str_replace('Y', '*', $_GET['trame']);
	$trame = str_replace('Z', '#', $trame);
	log::add ('myhome','event','Receive to Jeedom : '.$trame);
	
	$tramedecrypt=myhome::decrypt_trame($trame);
	log::add('myhome', 'debug', 'Jeemyhome_Equipement : ' . print_r($tramedecrypt, true));
	
	foreach ($tramedecrypt as $key => $value) {
				if (is_null($value)) {
					$tramedecrypt[$key] = "NULL";
				} else {
					$tramedecrypt[$key] = $value;
				}
	}
	
	
	if ($tramedecrypt["format"]=="ACK" || $tramedecrypt["format"]=="NACK"){
		log::add ('myhome', 'debug', "Jeemyhome_Trame non interprétée");
	}
	
	if ($tramedecrypt["format"]!="ACK" && $tramedecrypt["format"]!="NACK"){			
		$myhome = myhome::byLogicalId($tramedecrypt["id"], 'myhome');
		if (!is_object($myhome)) {
				log::add('myhome', 'debug', 'Jeemyhome_Aucun équipement trouvé pour : ' . $tramedecrypt["id"]. " Création de l'equipement\n");
				$myhome = myhome::createFromDef($tramedecrypt);
				if (!is_object($myhome)) {
					log::add('myhome', 'debug', 'Jeemyhome_Aucun équipement trouvé pour : ' . $tramedecrypt["id"]." Erreur lors de la création de l'équipement\n" );
					die();
				}
		} elseif (is_object($myhome) && $tramedecrypt['format']=="BUS_COMMAND"){
			log::add('myhome', 'debug', "Jeemyhome_BUS_COMMAND \n");
			myhome::updateStatus($tramedecrypt);
			log::add('myhome', 'event', "Jeemyhome_update status");
			
		} else if (is_object($myhome) && $tramedecrypt['format']=="STATUS_REQUEST"){
			log::add('myhome', 'debug', "Jeemyhome_STATUS_REQUEST, Aucun action effectuée \n");
			//myhome::updateRequestStatus($tramedecrypt);
		}else if (is_object($myhome) && $tramedecrypt['format']=="DIMENSION_SET"){
			log::add('myhome', 'debug', "Jeemyhome_DIMENSION_SET, mise a jour des statuts \n");
			myhome::updateStatus($tramedecrypt);
		}else if (is_object($myhome) && $tramedecrypt['format']=="DIMENSION_REQUEST" && isset($tramedecrypt['param'])){
			log::add('myhome', 'debug', "Jeemyhome_DIMENSION_REQUEST avec Parametres, mise a jour des statuts \n");
			//myhome::dimensionRequestStatus($tramedecrypt);
		}
	}
}
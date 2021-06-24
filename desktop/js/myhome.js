
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

 $('#bt_healthmyhome').on('click', function () {
    $('#md_modal').dialog({title: "{{Santé myhome}}"});
    $('#md_modal').load('index.php?v=d&plugin=myhome&modal=health').dialog('open');
});

$("#table_cmd").sortable({axis: "y", cursor: "move", items: ".cmd", placeholder: "ui-state-highlight", tolerance: "intersect", forcePlaceholderSize: true});

$('body').delegate('.cmdAttr[data-l1key=type]','change',function(){
	var tr = $(this).closest('tr');
	if ( $(this).value() =="info") {
		tr.find('.cmdAttr[data-l1key=configuration][data-l2key=whatdim]').hide()
		tr.find('.cmdAttr[data-l1key=configuration][data-l2key=where]').hide()
		tr.find('.cmdAttr[data-l1key=configuration][data-l2key=DureeCmd]').show()
	} else  if ( $(this).value() =="action") {
		tr.find('.cmdAttr[data-l1key=configuration][data-l2key=whatdim]').show()
		tr.find('.cmdAttr[data-l1key=configuration][data-l2key=where]').show()
		tr.find('.cmdAttr[data-l1key=configuration][data-l2key=DureeCmd]').hide()
	}
});

function printEqLogic(_id) {
	$.ajax({// fonction permettant de faire de l'ajax
        type: "POST", // methode de transmission des données au fichier php
        url: "plugins/myhome/core/ajax/myhome.ajax.php", // url du fichier php
        data: {
            action: "checktemplate",
            id: $('.eqLogicAttr[data-l1key=logicalId]').value(),
        },
        dataType: 'json',
        error: function (request, status, error) {
            handleAjaxError(request, status, error);
        },
        success: function (data_init) { // si l'appel a bien fonctionné
			if (data_init.state != 'ok') {
				$('#div_DashboardAlert').showAlert({message: data_init.result, level: 'danger'});
				return;
			}else{
				document.getElementById("iddec").innerHTML = data_init.result['iddec'];
				document.getElementById("iddec").readOnly = true;
				document.getElementById("iddec").style.backgroundColor  = "#dedede";
				$('#vdispo').append(data_init.result['version']);
				$('#rnotes').append(data_init.result['update']);
				if (data_init.result['versioninst'] < data_init.result['version']) {
					$('#vinst').css({'background-color': '#ff4343'});
				}else{
					$('#vinst').css({'background-color': ''});
				}
			}
		}
	});
}

function addCmdToTable(_cmd) {
    if (!isset(_cmd)) {
        var _cmd = {configuration: {}};
    }
	
	var selWhatDim = '<select style="width : 120px; margin-top : 5px;" class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="whatdim">';
	
	if (isset(_cmd.configuration.whatdim)) {
		selWhatDim += '<option value={"what":"' + _cmd.configuration.whatdim.what + '","dim":"' + _cmd.configuration.whatdim.dim + '","nom":"' + _cmd.configuration.whatdim.nom + '"}>{{' + _cmd.configuration.whatdim.nom + '}}</option>';
	} else {
		selWhatDim += '<option value="">Aucune</option>';
	}
	
	if ($('.eqLogicAttr[data-l1key=category][data-l2key=light]').value()==1) {
	
		
		//Commande What pour lumiere
		selWhatDim += '<option value={"what":"0","dim":"NULL","nom":"Off"}>{{Off}}</option>';
		selWhatDim += '<option value={"what":"1","dim":"NULL","nom":"On"}>{{On}}</option>';
		selWhatDim += '<option value={"what":"2","dim":"NULL","nom":"20%"}>{{20%}}</option>';
		selWhatDim += '<option value={"what":"3","dim":"NULL","nom":"30%"}>{{30%}}</option>';
		selWhatDim += '<option value={"what":"4","dim":"NULL","nom":"40%"}>{{40%}}</option>';
		selWhatDim += '<option value={"what":"5","dim":"NULL","nom":"50%"}>{{50%}}</option>';
		selWhatDim += '<option value={"what":"6","dim":"NULL","nom":"60%"}>{{60%}}</option>';
		selWhatDim += '<option value={"what":"7","dim":"NULL","nom":"70%"}>{{70%}}</option>';
		selWhatDim += '<option value={"what":"8","dim":"NULL","nom":"80%"}>{{80%}}</option>';
		selWhatDim += '<option value={"what":"9","dim":"NULL","nom":"90%"}>{{90%}}</option>';
		selWhatDim += '<option value={"what":"10","dim":"NULL","nom":"100%"}>{{100%}}</option>';
		
		//Commande Dimension pour lumiere
		selWhatDim += '<option value={"what":"NULL","dim":"1","nom":"Light_Statut_Request"}>{{Light_Statut_Request}}</option>';
		selWhatDim += '<option value={"what":"NULL","dim":"#1","nom":"Get/Set_Dimming_level_and_speed"}>{{Get/Set_Dimming_level_and_speed}}</option>';
	
	} 
		
		//Commande What pour Management
		selWhatDim += '<option value={"what":"22","dim":"NULL","nom":"Who13-Reset_Device"}>{{Who13-Reset_Device}}</option>';
		selWhatDim += '<option value={"what":"30","dim":"NULL","nom":"Who13-Create_Network"}>{{Who13-Create_Network}}</option>';
		selWhatDim += '<option value={"what":"31","dim":"NULL","nom":"Who13-Close_Network"}>{{Who13-Close_Network}}</option>';
		selWhatDim += '<option value={"what":"32","dim":"NULL","nom":"Who13-Open_network"}>{{Who13-Open_network}}</option>';
		selWhatDim += '<option value={"what":"33","dim":"NULL","nom":"Who13-Join_Network"}>{{Who13-Join_Network}}</option>';
		selWhatDim += '<option value={"what":"34","dim":"NULL","nom":"Who13-Leave_Network"}>{{Who13-Leave_Network}}</option>';
		selWhatDim += '<option value={"what":"60","dim":"NULL","nom":"Who13-Keep_Connect"}>{{Who13-Keep_Connect}}</option>';
		selWhatDim += '<option value={"what":"65","dim":"NULL","nom":"Who13-Scan"}>{{Who13-Scan}}</option>';
		selWhatDim += '<option value={"what":"66","dim":"NULL","nom":"Who13-Supervisor"}>{{Who13-Supervisor}}</option>';
		
		//Commande Dimension pour Managemennt
		selWhatDim += '<option value={"what":"NULL","dim":"12","nom":"Who13-MAC_Address"}>{{Who13-MAC_Address}}</option>';
		selWhatDim += '<option value={"what":"NULL","dim":"16","nom":"Who13-Firmware_Version"}>{{Who13-Firmware_Version}}</option>';
		selWhatDim += '<option value={"what":"NULL","dim":"17","nom":"Who13-Hardware_Version"}>{{Who13-Hardware_Version}}</option>';
		selWhatDim += '<option value={"what":"NULL","dim":"26","nom":"Who13-Who_Implemented"}>{{Who13-Who_Implemented}}</option>';
		selWhatDim += '<option value={"what":"NULL","dim":"66","nom":"Who13-Product_Information"}>{{Who13-Product_Information}}</option>';
		selWhatDim += '<option value={"what":"NULL","dim":"67","nom":"Who13-Get_Number_of_Network_Product"}>{{Who13-Get_Number_of_Network_Product}}</option>';
		selWhatDim += '<option value={"what":"NULL","dim":"70","nom":"Who13-Identify"}>{{Who13-Identify}}</option>';
		selWhatDim += '<option value={"what":"NULL","dim":"71","nom":"Who13-Zigbee_Channel"}>{{Who13-Zigbee_Channel}}</option>';
		
		//Commande What pour Commande Scenario
		selWhatDim += '<option value={"what":"1","dim":"NULL","nom":"Who0-Scenario_X"}>{{Who0-Scenario_X}}</option>';
		selWhatDim += '<option value={"what":"40","dim":"NULL","nom":"Who0-Start_Recording_Scenario"}>{{Who0-Start_Recording_Scenario}}</option>';
		selWhatDim += '<option value={"what":"41","dim":"NULL","nom":"Who0-End_Recording_Scenario"}>{{Who0-End_Recording_Scenario}}</option>';
		selWhatDim += '<option value={"what":"42","dim":"NULL","nom":"Who0-Erase_All_Scenario"}>{{Who0-Erase_All_Scenario}}</option>';
		selWhatDim += '<option value={"what":"42","dim":"NULL","nom":"Who0-Erase_Scenario_X"}>{{Who0-Erase_Scenario_X}}</option>';
		
	selWhatDim += '</select>';
    
    var tr = '<tr class="cmd" data-cmd_id="' + init(_cmd.id) + '">';
    tr += '<td>';
    tr += '<div class="row">';
    tr += '<div class="col-sm-6">';
    tr += '<a class="cmdAction btn btn-default btn-sm" data-l1key="chooseIcon"><i class="fa fa-flag"></i> Icône</a>';
    tr += '<span class="cmdAttr" data-l1key="display" data-l2key="icon" style="margin-left : 10px;"></span>';
    tr += '</div>';
    tr += '<div class="col-sm-6">';
    tr += '<input class="cmdAttr form-control input-sm" data-l1key="name">';
	tr += '</div>';
    tr += '</div>';
	tr += '<select class="cmdAttr form-control tooltips input-sm" data-l1key="value" style="display : none;margin-top : 5px;" title="La valeur de la commande vaut par défaut la commande">';
    tr += '<option value="">Aucune</option>';
    tr += '</select>';
    tr += '</td>';
    tr += '<td>';
    tr += '<input class="cmdAttr form-control input-sm" data-l1key="id" style="display : none;">';
    tr += '<span class="type" type="' + init(_cmd.type) + '">' + jeedom.cmd.availableType() + '</span>';
    tr += '<span class="subType" subType="' + init(_cmd.subType) + '"></span>';
   	tr += '' + selWhatDim;
    tr += '</td>';
	tr += '<td><input class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="unit">';
    tr += '</td>';
	tr += '<td>';
    tr += '<select class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="where">';
	if (isset(_cmd.configuration.where)) {
		tr += '<option value="' + _cmd.configuration.where + '">' + _cmd.configuration.where + '</option>';
	} else {
		tr += '<option value="">Aucune</option>';
	}
	tr += '<option value="Unicast">Unicast</option>';
    tr += '<option value="Broadcast">Broadcast</option>';
	tr += '<option value="Multicast">Multicast</option>';
	tr += '</select>';
    tr += '</td>';
    tr += '<td><input class="cmdAttr form-control input-sm" data-l1key="logicalId"  value="0">';
	tr += '<input class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="DureeCmd" placeholder="{{Durée de la commande (en seconde)}}">';
    tr += '<input class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="returnStateValue" placeholder="{{Valeur retour d\'état}}" style="margin-top : 5px;">';
    tr += '<input class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="returnStateTime" placeholder="{{Durée avant retour d\'état (min)}}" style="margin-top : 5px;">';
    tr += '</td>';
    tr += '<td>';
    tr += '<span><label class="checkbox-inline"><input type="checkbox" class="cmdAttr checkbox-inline" data-l1key="isHistorized" checked/>{{Historiser}}</label></span>';
    tr += '<span><label class="checkbox-inline"><input type="checkbox" class="cmdAttr checkbox-inline" data-l1key="isVisible"  checked/>{{Afficher}}</label></span>';
    tr += '<span><label class="checkbox-inline"><input type="checkbox" class="cmdAttr checkbox-inline" data-l1key="display" data-l2key="invertBinary"/>{{Inverser}}</label></span> ';
    tr += '</td>';
    tr += '<td>';
	tr += '<select class="cmdAttr form-control tooltips input-sm" data-l1key="configuration" data-l2key="updateCmdId" style="display : none;margin-top : 5px;" title="Commande d\'information à mettre à jour">';
    tr += '<option value="">Aucune</option>';
    tr += '</select>';
    tr += '<input class="tooltips cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="updateCmdToValue" placeholder="Valeur de l\'information" style="display : none;margin-top : 5px;">';
    tr += '<input class="cmdAttr form-control tooltips input-sm" data-l1key="unite"  style="width : 100px;" placeholder="Unité" title="Unité">';
    tr += '<input class="tooltips cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="minValue" placeholder="Min" title="Min"> ';
    tr += '<input class="tooltips cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="maxValue" placeholder="Max" title="Max" style="margin-top : 5px;">';
    tr += '</td>';
    tr += '<td>';
    if (is_numeric(_cmd.id)) {
        tr += '<a class="btn btn-default btn-xs cmdAction" data-action="configure"><i class="fa fa-cogs"></i></a> ';
        tr += '<a class="btn btn-default btn-xs cmdAction" data-action="test"><i class="fa fa-rss"></i> Tester </a>';
    }
    tr += '<i class="fa fa-minus-circle pull-right cmdAction cursor" data-action="remove"></i></td>';
    tr += '</tr>';
    $('#table_cmd tbody').append(tr);
    var tr = $('#table_cmd tbody tr:last');
    jeedom.eqLogic.builSelectCmd({
        id: $('.eqLogicAttr[data-l1key=id]').value(),
        filter: {type: 'info'},
        error: function (error) {
            $('#div_alert').showAlert({message: error.message, level: 'danger'});
        },
        success: function (result) {
            tr.find('.cmdAttr[data-l1key=value]').append(result);
            tr.find('.cmdAttr[data-l1key=configuration][data-l2key=updateCmdId]').append(result);
            tr.setValues(_cmd, '.cmdAttr');
            jeedom.cmd.changeType(tr, init(_cmd.subType));
        }
    });
}

 $('.changeIncludeState').on('click', function () {
    var el = $(this);
    jeedom.config.save({
        plugin : 'myhome',
        configuration: {autoDiscoverEqLogic: el.attr('data-state')},
        error: function (error) {
          $('#div_alert').showAlert({message: error.message, level: 'danger'});
      },
      success: function () {
        if (el.attr('data-state') == 1) {
            $.hideAlert();
            $('.changeIncludeState:not(.card)').removeClass('btn-default').addClass('btn-success');
            $('.changeIncludeState').attr('data-state', 0);
            $('.changeIncludeState.card').css('background-color','#8000FF');
            $('.changeIncludeState.card span center').text('{{Arrêter l\'inclusion}}');
            $('.changeIncludeState:not(.card)').html('<i class="fa fa-sign-in fa-rotate-90"></i> {{Arreter inclusion}}');
            $('#div_inclusionAlert').showAlert({message: '{{Vous etes en mode inclusion. Recliquez sur le bouton d\'inclusion pour sortir de ce mode}}', level: 'warning'});
        } else {
            $.hideAlert();
            $('.changeIncludeState:not(.card)').addClass('btn-default').removeClass('btn-success btn-danger');
            $('.changeIncludeState').attr('data-state', 1);
            $('.changeIncludeState:not(.card)').html('<i class="fa fa-sign-in fa-rotate-90"></i> {{Mode inclusion}}');
            $('.changeIncludeState.card span center').text('{{Mode inclusion}}');
            $('.changeIncludeState.card').css('background-color','#ffffff');
            $('#div_inclusionAlert').hideAlert();
        }
    }
});
});

$('body').on('myhome::includeDevice', function (_event,_options) {
    if (modifyWithoutSave) {
        $('#div_inclusionAlert').showAlert({message: '{{Un périphérique vient d\'être inclu/exclu. Veuillez réactualiser la page}}', level: 'warning'});
    } else {
        if (_options == '') {
            window.location.reload();
        } else {
            window.location.href = 'index.php?v=d&p=myhome&m=myhome&id=' + _options;
        }
    }
});
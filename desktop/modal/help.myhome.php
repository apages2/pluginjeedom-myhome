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
?>



<div class="panel-group" id="accordion">

    <div class="panel panel-default">
        <div class="panel-heading">
            <h4 class="panel-title">
                <a class="accordion-toggle" data-toggle="collapse" data-parent="#accordion" href="#collapse_condition">
                    Prises
                </a>
            </h4>
        </div>
        <div id="collapse_condition" class="panel-collapse collapse">
            <div class="panel-body">
                <h4>A mettre dans le champs "Logical ID (info) ou Commande brute (action)" : </h4>
                <pre>On : 0B110000#ID#09010F90
Off : 0B110000#ID#09000090</pre>
                <div class='alert alert-danger'>N'oubliez pas de remplir le ID de l'équipement</div>
                <div class='alert alert-warning'>Creer l'équipement avec la commande On et Off, branchez la prise, appuyer sur son bouton d'aprentissage et sur Jeedom appuyer sur test au niveau de la commande On.</div>
            </div>
        </div>
    </div>
</div>
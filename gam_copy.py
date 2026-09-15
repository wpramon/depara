from googleads import ad_manager
from googleads import oauth2
from copy import deepcopy

NETWORK_CODE = "95377733"
KEY_FILE = "service-account.json"
API_VERSION = "v202505"


def get_client():

    oauth_client = oauth2.GoogleServiceAccountClient(
        KEY_FILE,
        oauth2.GetAPIScope(
            "ad_manager"
        )
    )

    return ad_manager.AdManagerClient(
        oauth_client,
        "LineItemCopyTool",
        network_code=NETWORK_CODE
    )


def get_line_item(
    line_item_service,
    line_item_id
):

    statement = {
        "query":
        f"WHERE id = {line_item_id}"
    }

    response = (
        line_item_service
        .getLineItemsByStatement(
            statement
        )
    )

    if not response.get(
        "results"
    ):
        raise Exception(
            f"Line Item "
            f"{line_item_id} "
            f"não encontrado"
        )

    return response[
        "results"
    ][0]


def copiar_configuracao(
    source_id,
    target_id
):

    client = get_client()

    line_item_service = (
        client.GetService(
            "LineItemService",
            version=API_VERSION
        )
    )

    lica_service = (
        client.GetService(
            "LineItemCreativeAssociationService",
            version=API_VERSION
        )
    )

    source = get_line_item(
        line_item_service,
        source_id
    )

    target = get_line_item(
        line_item_service,
        target_id
    )

    fields_to_copy = [

        "targeting",

        "creativePlaceholders",

        "deliveryRateType",

        "environmentType",

        "roadblockingType",

        "creativeRotationType",

        "frequencyCaps",

        "allowOverbook",

        "skipInventoryCheck",

        "appliedLabels",

        "companionDeliveryOption",

        "deliveryForecastSource"
    ]

    for field in fields_to_copy:

        if field in source:

            target[field] = (
                deepcopy(
                    source[field]
                )
            )

    line_item_service.updateLineItems(
        [target]
    )

    source_statement = {
        "query":
        f"WHERE lineItemId = {source_id}"
    }

    source_licas = (
        lica_service
        .getLineItemCreativeAssociationsByStatement(
            source_statement
        )
        .get(
            "results",
            []
        )
    )

    target_statement = {
        "query":
        f"WHERE lineItemId = {target_id}"
    }

    target_licas = (
        lica_service
        .getLineItemCreativeAssociationsByStatement(
            target_statement
        )
        .get(
            "results",
            []
        )
    )

    if target_licas:

        action = {

            "xsi_type":
            (
                "DeleteLineItemCreativeAssociations"
            )
        }

        lica_service.performLineItemCreativeAssociationAction(
            action,
            target_statement
        )

    novos_licas = []

    for lica in source_licas:

        novo = {

            "lineItemId":
            target_id,

            "creativeId":
            lica[
                "creativeId"
            ]
        }

        if "sizes" in lica:

            novo["sizes"] = (
                deepcopy(
                    lica["sizes"]
                )
            )

        novos_licas.append(
            novo
        )

    if novos_licas:

        lica_service.createLineItemCreativeAssociations(
            novos_licas
        )

    return (
        f"Configuração copiada "
        f"de {source_id} "
        f"para {target_id}"
    )
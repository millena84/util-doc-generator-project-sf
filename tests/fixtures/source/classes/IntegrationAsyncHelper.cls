public without sharing class IntegrationAsyncHelper {
    private static final String LEGADO = 'https://legado.exemplo.invalid/SENTINELA_URL_FIXA';

    @future(callout=true)
    public static void processOrdersAsync(List<Id> orderIds) {
        HttpRequest req = new HttpRequest();
        req.setEndpoint('callout:Minha_NC/v1/pedidos?token=SENTINELA_CALLOUT_PATH');
        // req.setEndpoint('callout:NC_Em_Comentario');
        req.setMethod('POST');
        System.debug(orderIds.size());
    }

    @Future
    public static void recalc(Set<String> keys) {
        HttpRequest req = new HttpRequest();
        req.setEndpoint('https://legado.exemplo.invalid/SENTINELA_URL_FIXA/recalc');
        System.debug(keys);
    }

    public static Integer helper() { return 1; }
}

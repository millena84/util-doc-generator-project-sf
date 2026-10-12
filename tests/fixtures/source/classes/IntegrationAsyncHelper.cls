public without sharing class IntegrationAsyncHelper {
    @future(callout=true)
    public static void processOrdersAsync(List<Id> orderIds) {
        System.debug(orderIds.size());
    }

    @Future
    public static void recalc(Set<String> keys) {
        System.debug(keys);
    }

    public static Integer helper() { return 1; }
}

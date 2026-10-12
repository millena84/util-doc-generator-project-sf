public class DailyOrderCleanupScheduler implements System.Schedulable {
    public void execute(SchedulableContext sc) {
        OrderCleanupBatch job = new OrderCleanupBatch();
        Database.executeBatch(job, 200);
    }

    public static String agendar() {
        return System.schedule('Limpeza Diaria de Pedidos', '0 0 1 * * ?', new DailyOrderCleanupScheduler());
    }
}

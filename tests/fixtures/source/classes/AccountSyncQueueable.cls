public class AccountSyncQueueable implements Queueable, Database.AllowsCallouts {
    private List<Account> accounts;
    private Boolean retry;

    public AccountSyncQueueable(List<Account> accounts, Boolean retry) {
        this.accounts = accounts;
        this.retry = retry;
    }

    public void execute(QueueableContext context) {
        System.attachFinalizer(new IntegrationFinalizerHandler());
        if (retry) {
            System.enqueueJob(new AccountSyncQueueable(accounts, false), 5);
        }
    }
}

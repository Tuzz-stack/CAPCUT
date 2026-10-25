/* Synthetic diagnostic only. No OpenCode/Kortix code or credentials. */
#define _GNU_SOURCE
#include <errno.h>
#include <pthread.h>
#include <semaphore.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

static sem_t thread_ready;
static sem_t handler_ready;
static int allow_trap;
static volatile sig_atomic_t suspended;

static void suspend_handler(int signal_number) {
    (void)signal_number;
    if (suspended) return;
    suspended = 1;
    sigset_t mask;
    sigfillset(&mask);
    sigdelset(&mask, SIGPWR);
    if (allow_trap) sigdelset(&mask, SIGTRAP);
    sem_post(&handler_ready);
    sigsuspend(&mask);
    suspended = 0;
}

static void *worker(void *unused) {
    (void)unused;
    sem_post(&thread_ready);
    for (;;) pause();
    return NULL;
}

static void wait_sem(sem_t *value) {
    while (sem_wait(value) != 0) {
        if (errno != EINTR) { perror("sem_wait"); exit(2); }
    }
}

int main(int argc, char **argv) {
    if (argc != 2 || (strcmp(argv[1], "plain") && strcmp(argv[1], "gc-wait") && strcmp(argv[1], "gc-wait-allow-trap"))) return 2;
    setvbuf(stdout, NULL, _IONBF, 0);
    allow_trap = !strcmp(argv[1], "gc-wait-allow-trap");
    sem_init(&thread_ready, 0, 0);
    sem_init(&handler_ready, 0, 0);
    struct sigaction action = {0};
    action.sa_handler = suspend_handler;
    action.sa_flags = SA_RESTART;
    sigemptyset(&action.sa_mask);
    sigaddset(&action.sa_mask, SIGPWR);
    if (sigaction(SIGPWR, &action, NULL)) { perror("sigaction"); return 2; }
    pthread_t thread;
    int error = pthread_create(&thread, NULL, worker, NULL);
    if (error) { fprintf(stderr, "pthread_create: %s\n", strerror(error)); return 2; }
    wait_sem(&thread_ready);
    if (strcmp(argv[1], "plain")) {
        if ((error = pthread_kill(thread, SIGPWR))) { fprintf(stderr, "pthread_kill: %s\n", strerror(error)); return 2; }
        wait_sem(&handler_ready);
        /* Let the handler reach sigsuspend before the bounded fork probe. */
        usleep(20000);
    }
    printf("BEFORE_FORK mode=%s pid=%d\n", argv[1], getpid());
    pid_t child = fork();
    if (child < 0) { perror("fork"); return 2; }
    if (!child) _exit(0);
    printf("AFTER_FORK child=%d\n", child);
    int status;
    while (waitpid(child, &status, 0) < 0) {
        if (errno != EINTR) { perror("waitpid"); return 2; }
    }
    if (!WIFEXITED(status) || WEXITSTATUS(status)) return 3;
    puts("PASS");
    return 0;
}

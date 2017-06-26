
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <mntent.h>
#include <unistd.h>
#include <errno.h>
#include <ctype.h>

static char *input_path = NULL;
static char *output_path = NULL;
static char *output_dev = NULL;
static char **list_output_dev = NULL;
static char *cmd = NULL;
static FILE *aFile = NULL;

void usage(char *name)
{
  printf("Usage: %s [-I <filepath>] [-O <mountpoint(s)> ]\n\n", name);
  printf("Mandatory options:\n");
  printf("\t-I: filepath binary to copy\n");
  printf("\t-O: mountpoint(s) destination name.\n");
  printf("\t    Could be a list (separated by','). Ex: \"NODE_1,NODE2,NODE_3\"\n");
}

void free_ressource()
{
  if(input_path)
    free(input_path);
  if(output_path)
    free(output_path);
  if(output_dev)
    free(output_dev);
  if(list_output_dev)
    free(list_output_dev);
  if(cmd)
    free(cmd);
  if(aFile)
    endmntent(aFile);
}

int main(int argc, char *argv[])
{
  int c, i;
  int ret = 0;
  int device_found = 0;
  struct mntent *ent = NULL;
  char *p = NULL;
  int n_output_dev = 0;
  char scp_cmd[]="scp";

  opterr = 0;

  while ((c = getopt (argc, argv, "I:O:")) != -1)
    switch (c)
      {
      case 'I':
        input_path = malloc(strlen(optarg)+1);
		if(input_path != NULL)
          strcpy(input_path, optarg);
        break;
      case 'O':
        output_dev = malloc(strlen(optarg)+1);
		if(output_dev != NULL)
          strcpy(output_dev, optarg);
        break;
      case '?':
        if ((optopt == 'I') || (optopt == 'O'))
          fprintf (stderr, "Option -%c requires an argument.\n", optopt);
        else if (isprint (optopt))
          fprintf (stderr, "Unknown option `-%c'.\n", optopt);
        else
          fprintf (stderr,
                   "Unknown option character `\\x%x'.\n",
                   optopt);
		usage(argv[0]);
        free_ressource();
        return EINVAL;
      default:
        abort ();
      }

  if((input_path == NULL) || (output_dev == NULL))
  {
    free_ressource();
	exit(ENOMEM);
  }

  if (strlen(input_path) && strlen(output_dev))
  {
    /* get the mounted devices list */
    aFile = setmntent("/proc/mounts", "r");
    if (aFile == NULL) {
      perror("setmntent");
      free_ressource();
      exit(ENOENT);
    }

	p = strtok (output_dev, ",\"");

    /* split output_dev and append tokens to list_output_dev */
    while (p) {
      list_output_dev = realloc (list_output_dev, sizeof (char*) * ++n_output_dev);

      if (list_output_dev == NULL)
        exit (ENOMEM);

      list_output_dev[n_output_dev-1] = p;

      p = strtok (NULL, ",\"");
    }

    /* realloc one extra element for the last NULL */
    list_output_dev = realloc (list_output_dev, sizeof (char*) * (n_output_dev+1));
    list_output_dev[n_output_dev] = 0;

	/* now lets read the path of the device */
    while ((NULL != (ent = getmntent(aFile))) && (!device_found)) {
      for (i = 0; (i < (n_output_dev)) && (!device_found); ++i) {
        if (strstr(ent->mnt_dir, list_output_dev[i])) {
          output_path = malloc(strlen(ent->mnt_dir)+1);
          if(output_path != NULL) {
            sprintf(output_path, "%s", ent->mnt_dir);
          } else {
            free_ressource();
            exit(ENOMEM);
          }
          device_found = 1;
        }
      }
    }

    if(device_found) {
      printf("copying %s to %s\n", input_path, output_path);
      cmd = malloc(strlen(scp_cmd)+1+strlen(input_path)+1+strlen(output_path)+1);
      if(cmd != NULL) {
        sprintf(cmd, "%s %s %s", scp_cmd, input_path, output_path);
      } else {
        free_ressource();
        exit(ENOMEM);
     }
     ret = system(cmd);

    } else {
      printf("%s not found. Please ensure the device is correctly connected\n",
                output_dev);
      ret = ENODEV;
    }
  }
  else
  {
    printf("Missing argument\n");
    usage(argv[0]);
  }
  free_ressource();
  return ret;
}

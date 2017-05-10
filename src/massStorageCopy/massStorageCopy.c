
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <mntent.h>
#include <unistd.h>

void usage(char *name)
{
  printf("Usage: %s [-I <filepath>] [-O <mountpoint> ]\n\n", name);
  printf("Mandatory options:\n");
  printf("\t-I: filepath binary to copy\n");
  printf("\t-O: mountpoint destination name\n");
}

int main(int argc, char *argv[])
{
  int c, i;
  int ret = 0;
  int device_found = 0;
  char input_path[256] = "";
  char output_dev[256] = "";
  char output_path[256] = "";
  char cmd[512] = "";
  struct mntent *ent = NULL;
  FILE *aFile = NULL;

  opterr = 0;

  while ((c = getopt (argc, argv, "I:O:")) != -1)
    switch (c)
      {
      case 'I':
        strcpy(input_path, optarg);
        break;
      case 'O':
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
        return 1;
      default:
        abort ();
      }

  if (strlen(input_path) && strlen(output_dev))
  {
    //get the mounted devives list
    aFile = setmntent("/proc/mounts", "r");
    if (aFile == NULL) {
      perror("setmntent");
      exit(1);
    }

    //now lets read the path of the device
    while (NULL != (ent = getmntent(aFile))) {
      if (strstr(ent->mnt_dir, output_dev)) {
        sprintf(output_path, "%s", ent->mnt_dir);
        device_found = 1;
      }
    }

    endmntent(aFile);

    if(device_found) {
      printf("copying %s to %s\n", input_path, output_path);

	  sprintf(cmd, "scp %s %s", input_path, output_path);
      system(cmd);

    } else {
      printf("%s not found. please ensure the device is correctly connected\n",
                output_dev);
      ret = -1;
    }
  }
  else
  {
    printf("Missing argument\n");
    usage(argv[0]);
  }

  return ret;
}

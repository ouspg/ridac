#include <stdio.h>

int main(int argc, char ** argv){

    char * filename = 0;
    FILE * complexfile = 0;
    long offset; 
    long number = 0;
    long i;

    if( argc != 4){
        printf("usage: %s FILENAME NUMBEROFSAMPLES OFFSET\n",argv[0]); 
        return 1;
    }

    filename = argv[1];

    if ( sscanf(argv[2], "%ld", &number) == 0){
        perror("something with the number of samples");
        return 1;
    }

    if ( sscanf(argv[3], "%ld", &offset) == 0){
        perror("something with the offset of the file");
        return 1;
    }

    complexfile = fopen(filename,"rb");
    if (complexfile == NULL){
        perror("something when reading the file");
        return 1;
    }

    printf("filename %s, number of samples %ld, offset %ld:\n\n",
        filename,
        number,
        offset
        );


    if (fseek(complexfile,offset * 2 * sizeof(float),SEEK_SET) != 0){
        perror("something when seeking the offset for the file");
        return 1;
    }


    for(i = 0;i< number;i ++){
        float a,b;
        if(fread(&a,sizeof(float),1,complexfile) == 0 ||
            fread(&b,sizeof(float),1,complexfile) == 0)
        {
            //TODO check if the other read succeed  .. 
            if(ferror(complexfile)){
                perror("Something occurred while reading the file");
            }
            if(feof(complexfile)) {
                printf("end of the file\n");
                }
            break;
        }
        printf("%f %f\n",a,b); 
    }

    fclose(complexfile);
    return 0;
}

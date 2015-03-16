#include <stdio.h>
#include <string.h>

//do not touch to the these -->
#define USE_COMPLEX 2
#define USE_FLOAT 1

#define FIND_RANGE 1
#define PRINT_DATA 2
//<--


//Uglyglobals for fileActions. Stored here because no classes can be used in c.
//this would have been much easier with python's yield also.

long numberOfPrinted = 0;
long numberOfSamples = 0;
float minValuer = 0;
float maxValuer = 0;
float minValuei = 0;
float maxValuei = 0;

long width = 0;

void fileActions(float r, float i, int action, int isComplex)
{
  int forAbs;
  if(action == FIND_RANGE){
    if( numberOfSamples == 0){
      minValuer = r;
      maxValuer = r;
      minValuei = i;
      maxValuei = i;
    }
    if(minValuer > r) minValuer = r;
    if(minValuei > i) minValuei = i;
    if(maxValuer < r) maxValuer = r;
    if(maxValuei < i) maxValuei = i;
    numberOfSamples += 1;
    return;
  }
  if(action == PRINT_DATA){
    //abs for possible small negative values
    //fprintf(stderr,"%f %f\n",i,r);
    r = (r-minValuer)*255 / (maxValuer - minValuer);
    if (isComplex == USE_COMPLEX)
      i = (i-minValuei)*255 / (maxValuei - minValuei);
    //if(r< 0)
    //  fprintf(stderr,"%f --> %x\n",r,(unsigned char)r);
    //I like green and blue in that order so green = r and blue = i
    //fprintf(stderr,"%x %x\n",(unsigned char)i,(unsigned char)r);
    //forAbs = abs((int)r);
    putc((unsigned char)i,stdout);
    //forAbs = abs((int)i);
    putc((unsigned char)r,stdout);
    putc(0,stdout);//"%c%c%c",i,r,0x00);
    
    numberOfPrinted += 1;
    //the last row's padidng
    if(numberOfPrinted == numberOfSamples){
          for(i=0;i< 3*(width - (numberOfPrinted % width)); i+=1)
	    fputc(0x00,stdout);
    }
    //padding to the end of row
    if(numberOfPrinted% width == 0 || numberOfPrinted == numberOfSamples){
      for(i=0; i< (4 -(width*3)%4)%4; i+=1)
	fputc(0x00,stdout);

    }
    

    return; 
  }
}
  
void printHeader(){
  long height = 0;
  long fileSize = 0;
  long i = 0;
unsigned char rest[] = {0x01, 0x00, 0x18, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x13, 0x0B, 0x00, 0x00, 0x13, 0x0B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};

  printf("BM");

  fileSize = 
    //headers
    54 + 
    //pixels
    (numberOfSamples * 3) + 
    //line end paddings
    (numberOfSamples/width) * (width*3)%4 + 
    //last line has different amount of zeroes.. and it might be all black
    (width - numberOfSamples%width)*3 + (width*3)%4; 
  //file size is dword: 4 bytes of data and LSB first
  putc(fileSize%256,stdout);
  putc((fileSize/256)%256,stdout);
  putc((fileSize/256/256)%256,stdout);
  putc((fileSize/256/256/256)%256,stdout);
  
  putc(0x00,stdout);putc(0x00,stdout);
  putc(0x00,stdout);putc(0x00,stdout);

  putc(0x36,stdout);putc(0x00,stdout);
  putc(0x00,stdout);putc(0x00,stdout);


  putc(0x28,stdout);putc(0x00,stdout);
  putc(0x00,stdout);putc(0x00,stdout);
  
  //widht
  putc(width%256,stdout);
  putc((width/256)%256,stdout);
  putc((width/256/256)%256,stdout);
  putc((width/256/256/256)%256,stdout);

  //height .. the last line might be just black
  height = numberOfSamples / width +1;
  putc(height%256,stdout);
  putc((height/256)%256,stdout);
  putc((height/256/256)%256,stdout);
  putc((height/256/256/256)%256,stdout);
  

  //the rest.
  for(i=0;i<28;i+=1)
    putc(rest[i],stdout);
}

int fileReader(FILE * complexfile, long offset, long number, int isComplex, int action)
{
  long i;
  float a,b;
  if (fseek(complexfile,offset * isComplex * sizeof(float),SEEK_SET) != 0){
    perror("something when seeking the offset for the file");
    return 1;
  }


  for(i = 0;i< number;i ++){
    a = 0;
    b = 0;
    if(fread(&a,sizeof(float),1,complexfile) == 0 ||
       isComplex == USE_COMPLEX && fread(&b,sizeof(float),1,complexfile) == 0)
      {
	//TODO check if the other read succeed  .. 
	if(ferror(complexfile)){
	  perror("Something occurred while reading the file");
	  return 1;
	}
	if(feof(complexfile)) {
	  fprintf(stderr,"The end of the file reached after %ld read samples\n",i);
	}
	break;
      }
    fileActions(a, b, action,isComplex);
    //printf("%f %f\n",a,b); 
  }
  
  return 0;
}



int main(int argc, char ** argv){

    char * filename = 0;
    FILE * complexfile = 0;
    long offset = 0; 
    long number = 0;
    //long widht = 0; as global
    int isComplex = -1;
    int error = 0;
 

    if( argc != 6){
      printf("usage: %s -cf FILENAME NUMBEROFSAMPLES OFFSET WIDHTOFPICTURE > DESTINATIONFILE\n",argv[0]); 
      printf(" reads the file 2 times trough: finds the range of values and then prints normalised values as bmp-file\n");
      return 1;
    }
    if(strcmp(argv[1],"-c")==0)
      isComplex = USE_COMPLEX;
    if(strcmp(argv[1],"-f")==0)
      isComplex = USE_FLOAT;
    if(isComplex == 0){
      fprintf(stderr,"something with the format: %s\n",argv[1]);
      return 1;
    } 
      
    filename = argv[2];
    if ( sscanf(argv[3], "%ld", &number) == 0){
        perror("something with the number of samples");
        return 1;
    }

    if ( sscanf(argv[4], "%ld", &offset) == 0){
        perror("something with the offset of the file");
        return 1;
    }

    if ( sscanf(argv[5], "%ld", &width) == 0){
        perror("something with the width of the file");
        return 1;
    }


    complexfile = fopen(filename,"rb");
    if (complexfile == NULL){
        perror("something when reading the file");
        return 1;
    }

    fprintf(stderr,"filename %s, number of samples %ld, offset %ld, line width %ld:\n\n",
        filename,
        number,
	    offset,
	    width
        );
    
    while(error == 0){
      error = fileReader(complexfile,
			 offset,
			 number,
			 isComplex, 
			 FIND_RANGE);
      if(error!=0)
	break;
      fprintf(stderr,"minValuer %f maxValuer %f minValuei %f maxValuei %f\n",
	      minValuer,
	      maxValuer, 
	      minValuei,
	      maxValuei);

      printHeader();
      error = fileReader(complexfile,
			 offset,
			 number,
			 isComplex, 
			 PRINT_DATA);
      fprintf(stderr,"headers done\n");
      if(error!=0)
	break;
      break;
    }
    fclose(complexfile);
    return error;
}
